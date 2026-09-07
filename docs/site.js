const samples = {
  positive: { label: 'Positivo', confidence: '92%', color: '#b8f24b', signals: ['“claras”', '“útiles”'], explanation: 'El ejemplo contiene términos positivos asociados con claridad y utilidad.' },
  neutral: { label: 'Neutral', confidence: '81%', color: '#8b7cff', signals: ['“cubrió”', '“programa”'], explanation: 'El texto describe un hecho sin una valoración emocional marcada.' },
  negative: { label: 'Negativo', confidence: '88%', color: '#ff806c', signals: ['“difícil”', '“seguir”'], explanation: 'El ejemplo expresa una dificultad concreta relacionada con el ritmo.' }
};

document.querySelectorAll('.example').forEach((button) => {
  button.addEventListener('click', () => {
    const tone = button.dataset.tone;
    const sample = samples[tone];
    document.querySelectorAll('.example').forEach((item) => item.classList.remove('active'));
    button.classList.add('active');
    document.querySelector('#comment').value = button.dataset.text;
    const badge = document.querySelector('#tone-badge');
    badge.className = `tone ${tone}`;
    badge.textContent = sample.label;
    document.querySelector('#confidence-value').textContent = sample.confidence;
    document.querySelector('#ring').style.setProperty('--tone', sample.color);
    document.querySelector('#signals').innerHTML = sample.signals.map((signal) => `<li>${signal}</li>`).join('');
    document.querySelector('#explanation').textContent = sample.explanation;
  });
});
