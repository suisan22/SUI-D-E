// 1. IMPORT FIREBASE MODULES
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.11.0/firebase-app.js";
import { getDatabase, ref, onValue, push } from "https://www.gstatic.com/firebasejs/10.11.0/firebase-database.js";

// 2. INITIALIZE FIREBASE (Replace with your actual config from Firebase console)
const firebaseConfig = {
    apiKey: "YOUR_API_KEY",
    authDomain: "YOUR_PROJECT_ID.firebaseapp.com",
    databaseURL: "https://suieliminateai-default-rtdb.firebaseio.com/",
    projectId: "YOUR_PROJECT_ID",
    storageBucket: "YOUR_PROJECT_ID.appspot.com",
    messagingSenderId: "YOUR_ID",
    appId: "YOUR_APP_ID"
};

const app = initializeApp(firebaseConfig);
const db = getDatabase(app);

// 3. TABLE UPDATE FUNCTION
function updateTable(threatList) {
    const body = document.getElementById('threatBody');
    if (!body) return;
    
    body.innerHTML = threatList.slice().reverse().map(t => `
        <tr class="${t.isIllegal ? 'bg-red-950/20' : 'bg-green-950/20'}">
            <td class="px-6 py-4">${t.url}</td>
            <td class="px-6 py-4 font-bold ${t.isIllegal ? 'text-red-500' : 'text-green-500'}">
                ${t.isIllegal ? '⚠️ ILLEGAL CONTENT' : '✅ SAFE'}
            </td>
        </tr>
        <tr class="bg-slate-900/50">
            <td colspan="2" class="px-6 py-2 text-xs text-slate-400 italic">Reason: ${t.reason}</td>
        </tr>
    `).join('');
}

// 4. FIREBASE LISTENER
function initFirebaseListener() {
    const threatsRef = ref(db, 'threats/');
    onValue(threatsRef, (snapshot) => {
        const data = snapshot.val();
        if (data) updateTable(Object.values(data));
    });
}

// 5. SCAN URL FUNCTION
async function scanUrl() {
    const url = document.getElementById('urlInput').value;
    if (!url) return alert("Enter a URL!");

    const body = document.getElementById('threatBody');
    body.innerHTML = '<tr><td colspan="2" class="px-6 py-8 text-center text-blue-400 animate-pulse">Analyzing...</td></tr>';

    try {
        const response = await fetch('http://127.0.0.1:8000/scan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url })
        });
        
        const result = await response.json();

        body.innerHTML = `
            <tr class="${result.isIllegal ? 'bg-red-950/20' : 'bg-green-950/20'}">
                <td class="px-6 py-4">${url}</td>
                <td class="px-6 py-4 font-bold ${result.isIllegal ? 'text-red-500' : 'text-green-500'}">
                    ${result.isIllegal ? '⚠️ ILLEGAL CONTENT' : '✅ SAFE'}
                </td>
            </tr>
            <tr class="bg-slate-900/50">
                <td colspan="2" class="px-6 py-2 text-xs text-slate-400 italic">Reason: ${result.reason}</td>
            </tr>
        `;

        // Push to Firebase using the globally available 'push' and 'ref'
        await push(ref(db, 'threats/'), {
            url: url,
            isIllegal: result.isIllegal,
            reason: result.reason,
            timestamp: Date.now()
        });

    } catch (error) {
        body.innerHTML = '<tr><td colspan="2" class="px-6 py-4 text-center text-red-500">Error processing data.</td></tr>';
    }
}

// 6. IMAGE FORENSICS FUNCTION
async function analyzeImage() {
    const fileInput = document.getElementById('imageInput');
    const file = fileInput.files[0];
    if (!file) return alert("Please select an image!");

    const resultsDiv = document.getElementById('imageResults');
    resultsDiv.innerHTML = "Searching the web...";

    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch('http://127.0.0.1:8000/analyze-image', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.found) {
            resultsDiv.innerHTML = "<strong>Matches found:</strong><br>" + 
                data.urls.map(url => `<a href="${url}" target="_blank" class="text-blue-400 block truncate">${url}</a>`).join('');
        } else {
            resultsDiv.innerHTML = "No matches found. Unique image.";
        }
    } catch (error) {
        resultsDiv.innerHTML = "Error connecting to backend.";
    }
}

// 7. INITIALIZE
initFirebaseListener();

// Add these listeners at the end of script.js
document.getElementById('scanButton').addEventListener('click', scanUrl);
document.getElementById('analyzeButton').addEventListener('click', analyzeImage);