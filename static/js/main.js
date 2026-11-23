// ---------- Quiz countdown timer (only runs on the quiz page) ----------
function startQuizTimer() {
  const timerEl = document.getElementById("timer");
  const form = document.getElementById("quiz-form");
  if (!timerEl || !form) return;

  // The server tells us how many seconds are left, so refreshing the page does not reset the timer
  let secondsLeft = parseInt(timerEl.dataset.seconds, 10);
  const submitBtn = document.getElementById("submit-btn");

  function render() {
    const minutes = String(Math.floor(secondsLeft / 60)).padStart(2, "0");
    const seconds = String(secondsLeft % 60).padStart(2, "0");
    timerEl.textContent = `${minutes}:${seconds}`;
    timerEl.classList.toggle("warning", secondsLeft <= 60);
  }

  function submitQuiz() {
    submitBtn.disabled = true; // stop double submits
    form.submit();
  }

  render();
  const interval = setInterval(() => {
    secondsLeft -= 1;
    render();
    if (secondsLeft <= 0) {
      clearInterval(interval);
      submitQuiz(); // time is up: send whatever is answered so far
    }
  }, 1000);

  form.addEventListener("submit", () => {
    clearInterval(interval);
    submitBtn.disabled = true;
  });
}

// ---------- "3 / 5 answered" counter ----------
function trackAnswered() {
  const counter = document.getElementById("answered-count");
  const form = document.getElementById("quiz-form");
  if (!counter || !form) return;

  const total = form.querySelectorAll(".question").length;
  form.addEventListener("change", () => {
    const answered = form.querySelectorAll("input[type=radio]:checked").length;
    counter.textContent = `${answered} / ${total} answered`;
  });
}

// ---------- Fade out flash messages ----------
function autoHideMessages() {
  document.querySelectorAll(".message").forEach((msg) => {
    setTimeout(() => {
      msg.style.opacity = "0";
      setTimeout(() => msg.remove(), 500);
    }, 4000);
  });
}

document.addEventListener("DOMContentLoaded", () => {
  startQuizTimer();
  trackAnswered();
  autoHideMessages();
});
