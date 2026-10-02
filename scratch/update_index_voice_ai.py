import re

def update_app_py():
    with open("src/app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Add Voice AI button to Header
    old_header_btn = '<button class="btn btn-sm btn-outline-warning text-white fw-bold rounded-pill px-3 me-1" onclick="showLoyaltyModal()"><i class="fa-solid fa-crown me-1 text-warning"></i> VIP Rewards</button>'
    new_header_btn = '''<button class="btn btn-sm btn-outline-info text-white fw-bold rounded-pill px-3 me-1" id="btnVoiceCommand" onclick="toggleVoiceCommand()"><i class="fa-solid fa-microphone text-info me-1" id="voiceMicIcon"></i> <span id="voiceBtnText">Voice AI</span></button>
                    <button class="btn btn-sm btn-outline-warning text-white fw-bold rounded-pill px-3 me-1" onclick="showLoyaltyModal()"><i class="fa-solid fa-crown me-1 text-warning"></i> VIP Rewards</button>'''

    if old_header_btn in content:
        content = content.replace(old_header_btn, new_header_btn)
        print("Added Voice AI button to Header!")
    else:
        print("Could not find old_header_btn in app.py!")

    # 2. Add Voice Feedback Toast HTML
    old_banner = '<div id="offlineSyncBanner" class="alert alert-warning border-warning shadow-sm rounded-3 d-none mb-3" role="alert">'
    new_toast = '''<div id="voiceFeedbackToast" class="alert alert-info border-info shadow-lg rounded-3 d-none position-fixed bottom-0 end-0 m-4 z-3" style="max-width: 360px;">
            <div class="d-flex align-items-center gap-3">
                <i class="fa-solid fa-waveform text-info fs-3"></i>
                <div>
                    <strong class="d-block text-dark small">Voice AI Recognized</strong>
                    <div id="voiceRecognizedText" class="fw-bold text-primary small">"..."</div>
                </div>
            </div>
        </div>
        <div id="offlineSyncBanner" class="alert alert-warning border-warning shadow-sm rounded-3 d-none mb-3" role="alert">'''

    if old_banner in content:
        content = content.replace(old_banner, new_toast)
        print("Added voiceFeedbackToast HTML!")
    else:
        print("Could not find old_banner in app.py!")

    # 3. Add Voice AI JavaScript engine before script tag end
    voice_js_code = '''
        // --- Hands-Free Voice AI Command System ---
        let recognition = null;
        let isVoiceListening = false;

        function initVoiceRecognition() {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRecognition) {
                console.warn('Web Speech API is not supported in this browser.');
                return null;
            }

            const rec = new SpeechRecognition();
            rec.continuous = true;
            rec.interimResults = false;
            rec.lang = 'en-US';

            rec.onstart = function() {
                isVoiceListening = true;
                updateVoiceUi(true);
                speakVoiceFeedback("Voice AI active. Listening for commands.");
            };

            rec.onend = function() {
                if (isVoiceListening) {
                    try { rec.start(); } catch(e) {}
                } else {
                    updateVoiceUi(false);
                }
            };

            rec.onresult = function(event) {
                const lastIdx = event.results.length - 1;
                const transcript = event.results[lastIdx][0].transcript.trim().toLowerCase();
                console.log('Voice Command Received:', transcript);
                showVoiceFeedback(transcript);
                processVoiceCommand(transcript);
            };

            rec.onerror = function(event) {
                console.error('Voice Recognition Error:', event.error);
            };

            return rec;
        }

        function toggleVoiceCommand() {
            if (!recognition) {
                recognition = initVoiceRecognition();
            }

            if (!recognition) {
                return alert('Speech Recognition is not supported in your browser. Try Google Chrome or Safari!');
            }

            if (isVoiceListening) {
                isVoiceListening = false;
                recognition.stop();
                updateVoiceUi(false);
                speakVoiceFeedback("Voice AI stopped.");
            } else {
                try {
                    recognition.start();
                } catch(e) {
                    isVoiceListening = true;
                    updateVoiceUi(true);
                }
            }
        }

        function updateVoiceUi(listening) {
            const btn = document.getElementById('btnVoiceCommand');
            const icon = document.getElementById('voiceMicIcon');
            const text = document.getElementById('voiceBtnText');

            if (listening) {
                btn.className = 'btn btn-sm btn-danger text-white fw-bold rounded-pill px-3 me-1 shadow';
                icon.className = 'fa-solid fa-microphone-slash me-1';
                text.innerText = 'Listening...';
            } else {
                btn.className = 'btn btn-sm btn-outline-info text-white fw-bold rounded-pill px-3 me-1';
                icon.className = 'fa-solid fa-microphone text-info me-1';
                text.innerText = 'Voice AI';
            }
        }

        function showVoiceFeedback(text) {
            const toast = document.getElementById('voiceFeedbackToast');
            const label = document.getElementById('voiceRecognizedText');
            if (toast && label) {
                label.innerText = `"${text}"`;
                toast.classList.remove('d-none');
                setTimeout(() => toast.classList.add('d-none'), 4000);
            }
        }

        function speakVoiceFeedback(text) {
            if ('speechSynthesis' in window) {
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.rate = 1.0;
                utterance.pitch = 1.0;
                window.speechSynthesis.speak(utterance);
            }
        }

        function processVoiceCommand(cmd) {
            if (cmd.includes('call waiter') || cmd.includes('waiter')) {
                callWaiter();
                speakVoiceFeedback("Calling waiter to table number " + activeTable);
            } else if (cmd.includes('pay') || cmd.includes('checkout')) {
                showPaymentModal();
                speakVoiceFeedback("Opening online table payments modal");
            } else if (cmd.includes('split')) {
                showSplitBillModal();
                speakVoiceFeedback("Opening table split bill modal");
            } else if (cmd.includes('rewards') || cmd.includes('points') || cmd.includes('vip')) {
                showLoyaltyModal();
                speakVoiceFeedback("Opening VIP loyalty rewards studio");
            } else if (cmd.includes('grill')) {
                setKdsFilter('GRILL');
                speakVoiceFeedback("Filtering KDS by Grill station");
            } else if (cmd.includes('fryer')) {
                setKdsFilter('FRYER');
                speakVoiceFeedback("Filtering KDS by Fryer station");
            } else if (cmd.includes('bar')) {
                setKdsFilter('BAR');
                speakVoiceFeedback("Filtering KDS by Bar station");
            } else if (cmd.includes('all stations') || cmd.includes('show all')) {
                setKdsFilter('ALL');
                speakVoiceFeedback("Showing all kitchen stations");
            } else if (cmd.includes('bump order') || cmd.includes('ready order') || cmd.includes('order ready')) {
                const match = cmd.match(/\d+/);
                if (match) {
                    const orderNum = match[0];
                    const targetId = 'ORD-' + orderNum.padStart(4, '0');
                    advanceOrderStatus(targetId);
                    speakVoiceFeedback(`Order ${orderNum} marked ready`);
                }
            } else if (cmd.startsWith('search ')) {
                const query = cmd.replace('search ', '').trim();
                const searchInput = document.getElementById('menuSearchInput');
                if (searchInput) {
                    searchInput.value = query;
                    filterMenu();
                    speakVoiceFeedback(`Filtered menu for ${query}`);
                }
            }
        }
'''

    target_script_end = "    </script>\n</body>\n</html>\"\"\""
    if target_script_end in content:
        content = content.replace(target_script_end, voice_js_code + "\n" + target_script_end)
        print("Added Voice AI JS functions before script end!")
    else:
        print("Could not find target_script_end in app.py!")

    with open("src/app.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    update_app_py()
