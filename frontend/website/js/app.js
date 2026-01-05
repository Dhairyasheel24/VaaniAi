// js/app.js
const languages = [
    { code: "en", name: "English" }, { code: "hi", name: "Hindi (हिंदी)" },
    { code: "mr", name: "Marathi (मराठी)" }, { code: "bn", name: "Bengali (বাংলা)" },
    { code: "gu", name: "Gujarati (ગુજરાતી)" }, { code: "kn", name: "Kannada (ಕನ್ನಡ)" },
    { code: "ml", name: "Malayalam (മലയാളം)" }, { code: "pa", name: "Punjabi (ਪੰਜਾਬੀ)" },
    { code: "ta", name: "Tamil (தமிழ்)" }, { code: "te", name: "Telugu (తెలుగు)" },
    { code: "ur", name: "Urdu (اردو)" }, { code: "es", name: "Spanish" },
    { code: "fr", name: "French" }, { code: "de", name: "German" },
    { code: "ja", name: "Japanese" }, { code: "ru", name: "Russian" },
    { code: "ar", name: "Arabic" }
];

const state = { isRecording: false };
const recorder = new VoiceRecorder();
let historyData = JSON.parse(localStorage.getItem('vaaniHistory')) || [];

const ui = {
    btn: document.getElementById('recordBtn'),
    swapBtn: document.getElementById('swapBtn'),
    replayBtn: document.getElementById('replayBtn'),
    status: document.getElementById('statusBadge'),
    loading: document.getElementById('loadingBar'),
    transcript: document.getElementById('transcriptText'),
    translation: document.getElementById('translationText'),
    sourceInput: document.getElementById('sourceLang'),
    targetInput: document.getElementById('targetLang'),
    audio: document.getElementById('audioPlayer'),
    
    // Dropdowns
    sourceTrigger: document.getElementById('sourceTrigger'),
    sourceOptions: document.querySelector('#sourceSelectWrapper .custom-options'),
    sourceLabel: document.getElementById('sourceLangLabel'),
    targetTrigger: document.getElementById('targetTrigger'),
    targetOptions: document.querySelector('#targetSelectWrapper .custom-options'),
    targetLabel: document.getElementById('targetLangLabel'),

    // History
    historyBtn: document.getElementById('historyBtn'),
    historyPanel: document.getElementById('historyPanel'),
    closeHistory: document.getElementById('closeHistory'),
    historyList: document.getElementById('historyList'),
    clearHistory: document.getElementById('clearHistory')
};

function init() {
    renderDropdowns();
    renderHistory();
    setupEventListeners();
}

function renderDropdowns() {
    const list = languages.map(l => `<div class="option" onclick="selectLang(this, '${l.code}', '${l.name}')">${l.name}</div>`).join('');
    ui.sourceOptions.innerHTML = list;
    ui.targetOptions.innerHTML = list;
}

function setupEventListeners() {
    ui.sourceTrigger.onclick = (e) => { e.stopPropagation(); toggleDropdown(ui.sourceOptions); };
    ui.targetTrigger.onclick = (e) => { e.stopPropagation(); toggleDropdown(ui.targetOptions); };
    document.onclick = () => closeAllDropdowns();

    ui.swapBtn.onclick = swapLanguages;
    ui.historyBtn.onclick = () => ui.historyPanel.classList.remove('hidden');
    ui.closeHistory.onclick = () => ui.historyPanel.classList.add('hidden');
    ui.clearHistory.onclick = clearHistory;

    ui.btn.onmousedown = startFlow;
    ui.btn.onmouseup = endFlow;
    ui.btn.ontouchstart = (e) => { e.preventDefault(); startFlow(); };
    ui.btn.ontouchend = (e) => { e.preventDefault(); endFlow(); };
    ui.replayBtn.onclick = () => ui.audio.play();
}

// Logic
function toggleDropdown(el) {
    closeAllDropdowns();
    el.classList.toggle('open');
}
function closeAllDropdowns() {
    ui.sourceOptions.classList.remove('open');
    ui.targetOptions.classList.remove('open');
}
window.selectLang = function(el, code, name) {
    const parent = el.closest('.custom-select-wrapper');
    if (parent.id === 'sourceSelectWrapper') {
        ui.sourceInput.value = code;
        ui.sourceLabel.textContent = name;
    } else {
        ui.targetInput.value = code;
        ui.targetLabel.textContent = name;
    }
}

function swapLanguages() {
    // Swap Code & Label
    [ui.sourceInput.value, ui.targetInput.value] = [ui.targetInput.value, ui.sourceInput.value];
    [ui.sourceLabel.textContent, ui.targetLabel.textContent] = [ui.targetLabel.textContent, ui.sourceLabel.textContent];
    
    // Swap Text
    if (!ui.transcript.classList.contains('placeholder')) {
        [ui.transcript.textContent, ui.translation.textContent] = [ui.translation.textContent, ui.transcript.textContent];
    }
}

async function startFlow() {
    if (state.isRecording) return;
    state.isRecording = true;
    ui.btn.classList.add('recording');
    ui.status.textContent = "Listening...";
    ui.transcript.classList.remove('placeholder');
    ui.transcript.textContent = "Listening...";
    await recorder.start();
}

async function endFlow() {
    if (!state.isRecording) return;
    state.isRecording = false;
    ui.btn.classList.remove('recording');
    ui.status.textContent = "Thinking...";
    ui.loading.classList.remove('hidden');

    try {
        const audioData = await recorder.stop();
        const stt = await API.stt(audioData, ui.sourceInput.value);
        ui.transcript.textContent = stt.text;

        const trans = await API.translate(stt.text, ui.sourceInput.value, ui.targetInput.value);
        ui.translation.textContent = trans.translated_text;
        ui.translation.classList.remove('placeholder');

        addToHistory(stt.text, trans.translated_text);

        const tts = await API.tts(trans.translated_text, ui.targetInput.value);
        playAudio(tts.audio_base64);
        ui.replayBtn.disabled = false;
        ui.status.textContent = "Ready";
    } catch (e) {
        console.error(e);
        ui.transcript.textContent = "Error: " + e.message;
    } finally {
        ui.loading.classList.add('hidden');
    }
}

function playAudio(b64) {
    ui.audio.src = "data:audio/mp3;base64," + b64;
    ui.audio.play();
}

// History Logic
function addToHistory(src, tgt) {
    historyData.unshift({ src, tgt });
    if(historyData.length > 20) historyData.pop();
    localStorage.setItem('vaaniHistory', JSON.stringify(historyData));
    renderHistory();
}
function renderHistory() {
    if(historyData.length === 0) {
        ui.historyList.innerHTML = '<div class="empty-state">No history</div>';
        return;
    }
    ui.historyList.innerHTML = historyData.map(item => `
        <div class="history-item">
            <div class="history-source">${item.src}</div>
            <div class="history-target">${item.tgt}</div>
        </div>
    `).join('');
}
function clearHistory() {
    historyData = [];
    localStorage.removeItem('vaaniHistory');
    renderHistory();
}

init();