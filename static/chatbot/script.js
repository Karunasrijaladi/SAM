const queryEl=document.getElementById('query');
// Greet on page load
window.addEventListener('load',()=>{
  const greeting='Hi, I am SAM. Ask me anything about VNIW or upload marks to get suggestions!';
  addMsg(greeting,'bot');
  speechSynthesis.speak(new SpeechSynthesisUtterance(greeting));
});
const chatBox=document.getElementById('chat-box');
const sendBtn=document.getElementById('send');
const micBtn=document.getElementById('mic');
const perfForm=document.getElementById('perf-form');
const manualBtn=document.getElementById('manual-analyze');
const perfRes=document.getElementById('perf-result');

function addMsg(text,cls){const d=document.createElement('div');d.className='msg '+cls;d.textContent=text;chatBox.appendChild(d);chatBox.scrollTop=chatBox.scrollHeight;
  return d;}

function submitQuery(){const q=queryEl.value.trim();if(!q)return;addMsg(q,'user');queryEl.value='';fetch('/api/chat/',{method:'POST',headers:{'X-CSRFToken':Cookies.get('csrftoken')},body:new URLSearchParams({query:q})}).then(r=>r.json()).then(d=>{addMsg(d.answer,'bot');speechSynthesis.speak(new SpeechSynthesisUtterance(d.answer));});}

sendBtn.onclick=submitQuery;
queryEl.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();submitQuery();}});

let recognizing=false,recognition;
if('webkitSpeechRecognition'in window){recognition=new webkitSpeechRecognition();recognition.lang='en-US';recognition.continuous=false;recognition.onresult=e=>{queryEl.value=e.results[0][0].transcript;sendBtn.click();};recognition.onend=()=>{recognizing=false;micBtn.classList.remove('active');};}
micBtn.onclick=()=>{if(!recognition)return;recognizing?recognition.stop():(recognition.start(),recognizing=true,micBtn.classList.add('active'));};

function renderResult(d){let html=`<strong>Overall:</strong> ${d.overall}% (${d.overall_category})<br><em>${d.overall_tips}</em><hr>`;
  html+='<table><thead><tr><th>Subject</th><th>Score</th><th>Category</th><th>Tips</th></tr></thead><tbody>';
  d.subjects.forEach(s=>{html+=`<tr><td>${s.subject}</td><td>${s.score}</td><td>${s.category}</td><td>${s.tips}</td></tr>`});
  html+='</tbody></table>';
  perfRes.innerHTML=html;
}

perfForm.onsubmit=e=>{e.preventDefault();const f=document.getElementById('csv-file').files[0];if(!f)return;const fd=new FormData();fd.append('file',f);fetch('/api/analyze/',{method:'POST',body:fd}).then(r=>r.json()).then(renderResult);};

// --- Manual marks entry logic ---
const marksMap={};
const addBtn=document.getElementById('add-mark');
const subjInput=document.getElementById('subj');
const markInput=document.getElementById('mark');
const tableBody=document.querySelector('#marks-table tbody');

function refreshTable(){tableBody.innerHTML='';Object.entries(marksMap).forEach(([s,m])=>{const tr=document.createElement('tr');tr.innerHTML=`<td>${s}</td><td>${m}</td><td><button class='del' data-subj='${s}'>✖</button></td>`;tableBody.appendChild(tr);});}

addBtn.onclick=()=>{const s=subjInput.value.trim();const m=parseFloat(markInput.value);if(!s||isNaN(m))return;marksMap[s]=m;subjInput.value='';markInput.value='';refreshTable();};

tableBody.addEventListener('click',e=>{if(e.target.classList.contains('del')){const s=e.target.dataset.subj;delete marksMap[s];refreshTable();}});

manualBtn.onclick=()=>{if(!Object.keys(marksMap).length)return;fetch('/api/analyze/',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams({data:JSON.stringify(marksMap)})}).then(r=>r.json()).then(renderResult);}

// --- Tab switching between CSV / Manual panes ---
const tabs=document.querySelectorAll('.tab');
const panes=document.querySelectorAll('.pane');

tabs.forEach(tab=>{
  tab.addEventListener('click',()=>{
    tabs.forEach(t=>t.classList.remove('active'));
    panes.forEach(p=>p.classList.remove('active'));
    tab.classList.add('active');
    document.querySelector(tab.dataset.target).classList.add('active');
  });
});




