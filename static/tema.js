const raiz = document.documentElement;
const botao = document.getElementById('tema');

function aplicarTema(tema) {
  raiz.dataset.tema = tema;
  botao.textContent = tema === 'claro' ? '🌙' : '☀️';
}

let salvo = null;
try { salvo = localStorage.getItem('tema'); } catch (e) {}
const prefereClaro = window.matchMedia('(prefers-color-scheme: light)').matches;
aplicarTema(salvo || (prefereClaro ? 'claro' : 'escuro'));

botao.addEventListener('click', () => {
  const novo = raiz.dataset.tema === 'claro' ? 'escuro' : 'claro';
  aplicarTema(novo);
  try { localStorage.setItem('tema', novo); } catch (e) {}
});
