const textarea = document.querySelector('#comment');
const counter = document.querySelector('#character-count');

if (textarea && counter) {
  const updateCount = () => { counter.textContent = String(textarea.value.length); };
  textarea.addEventListener('input', updateCount);
  updateCount();
}
