/**
 * 🏫 Rate My Teacher - Front-End Interactivity
 * Handles star ratings, tag toggling, and asynchronous API calls.
 */

document.addEventListener("DOMContentLoaded", () => {
  setupStarRatings();
  setupTagSelectors();
  setupAddTeacherForm();
  setupReviewForm();
  setupVoteButtons();
});

// ==========================================================================
// 1. ⭐ STAR RATING WIDGET (Clickable & Hoverable Stars)
// ==========================================================================
function setupStarRatings() {
  const starContainers = document.querySelectorAll(".star-rating");

  starContainers.forEach((container) => {
    const stars = container.querySelectorAll(".star");
    const hiddenInput = container.querySelector("input[type='hidden']");

    stars.forEach((star) => {
      // Hover effect: highlight stars up to cursor
      star.addEventListener("mouseenter", () => {
        const val = parseInt(star.getAttribute("data-value"));
        highlightStars(stars, val);
      });

      // Mouse leave: restore the selected stars
      container.addEventListener("mouseleave", () => {
        const currentVal = parseInt(hiddenInput.value) || 0;
        highlightStars(stars, currentVal);
      });

      // Click: lock in the rating into the hidden input
      star.addEventListener("click", () => {
        const val = parseInt(star.getAttribute("data-value"));
        hiddenInput.value = val;
        highlightStars(stars, val);
      });
    });
  });
}

function highlightStars(stars, count) {
  stars.forEach((star) => {
    const starVal = parseInt(star.getAttribute("data-value"));
    if (starVal <= count) {
      star.classList.add("active");
      star.textContent = "⭐";
    } else {
      star.classList.remove("active");
      star.textContent = "☆";
    }
  });
}

// ==========================================================================
// 2. 🏷️ TAG CHIP TOGGLER (e.g., Fun Projects, Tough Grader)
// ==========================================================================
function setupTagSelectors() {
  const tagChips = document.querySelectorAll(".tag-chip");

  tagChips.forEach((chip) => {
    chip.addEventListener("click", () => {
      chip.classList.toggle("selected");
      const checkbox = chip.querySelector("input[type='checkbox']");
      if (checkbox) {
        checkbox.checked = chip.classList.contains("selected");
      }
    });
  });
}

// ==========================================================================
// 3. ➕ SUBMIT NEW TEACHER FORM (add_teacher.html)
// ==========================================================================
function setupAddTeacherForm() {
  const form = document.getElementById("add-teacher-form");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearAlerts();

    const submitBtn = form.querySelector("button[type='submit']");
    submitBtn.disabled = true;
    submitBtn.textContent = "Adding Teacher...";

    const payload = {
      school_id: form.querySelector("#school_id").value,
      first_name: form.querySelector("#first_name").value.trim(),
      last_name: form.querySelector("#last_name").value.trim(),
      department: form.querySelector("#department").value.trim(),
      grade_level: form.querySelector("#grade_level").value.trim(),
      bio: form.querySelector("#bio") ? form.querySelector("#bio").value.trim() : ""
    };

    // Client-side quick check
    if (!payload.school_id || !payload.first_name || !payload.last_name || !payload.department || !payload.grade_level) {
      showAlert("error", "⚠️ Please fill out all required fields before submitting.");
      submitBtn.disabled = false;
      submitBtn.textContent = "✅ Create Teacher Profile";
      return;
    }

    try {
      const response = await fetch("/api/teachers", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const result = await response.json();

      if (response.ok && result.success) {
        showAlert("success", "🎉 Success! New teacher profile created. Taking you to their page...");
        form.reset();
        setTimeout(() => {
          window.location.href = `/teacher/${result.teacher_id}`;
        }, 1500);
      } else {
        showAlert("error", `❌ ${result.error || "Failed to create teacher. Please try again."}`);
        submitBtn.disabled = false;
        submitBtn.textContent = "✅ Create Teacher Profile";
      }
    } catch (err) {
      showAlert("error", "🌐 Could not connect to the server. Make sure 'python dispatcher.py' is running!");
      submitBtn.disabled = false;
      submitBtn.textContent = "✅ Create Teacher Profile";
    }
  });
}

// ==========================================================================
// 4. ✍️ SUBMIT ANONYMOUS REVIEW FORM (teacher.html)
// ==========================================================================
function setupReviewForm() {
  const form = document.getElementById("review-form");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearAlerts();

    const teacherId = form.getAttribute("data-teacher-id");
    const overallInput = form.querySelector("#rating_overall");
    const diffInput = form.querySelector("#rating_difficulty");
    const helpInput = form.querySelector("#rating_helpfulness");
    const reviewTextInput = form.querySelector("#review_text");

    const ratingOverall = parseInt(overallInput.value) || 0;
    const ratingDiff = parseInt(diffInput.value) || 0;
    const ratingHelp = parseInt(helpInput.value) || 0;
    const reviewText = reviewTextInput.value.trim();

    // Friendly validation checks
    if (ratingOverall < 1 || ratingOverall > 5) {
      showAlert("error", "⭐ Please select an overall star rating (1 to 5).");
      return;
    }
    if (ratingDiff < 1 || ratingDiff > 5) {
      showAlert("error", "📊 Please select a difficulty rating (1 to 5).");
      return;
    }
    if (ratingHelp < 1 || ratingHelp > 5) {
      showAlert("error", "🤝 Please select a helpfulness rating (1 to 5).");
      return;
    }
    if (reviewText.length < 5) {
      showAlert("error", "✍️ Please write a few helpful words in your review comments.");
      return;
    }

    // Collect all selected tag IDs
    const selectedTagIds = [];
    form.querySelectorAll(".tag-chip.selected").forEach((chip) => {
      const tagId = chip.getAttribute("data-tag-id");
      if (tagId) selectedTagIds.push(parseInt(tagId));
    });

    const payload = {
      rating_overall: ratingOverall,
      rating_difficulty: ratingDiff,
      rating_helpfulness: ratingHelp,
      review_text: reviewText,
      course_name: form.querySelector("#course_name") ? form.querySelector("#course_name").value.trim() : "",
      reviewer_role: form.querySelector("input[name='reviewer_role']:checked") ? form.querySelector("input[name='reviewer_role']:checked").value : "student",
      student_grade_level: form.querySelector("#student_grade_level") ? form.querySelector("#student_grade_level").value : null,
      tag_ids: selectedTagIds
    };

    const submitBtn = form.querySelector("button[type='submit']");
    submitBtn.disabled = true;
    submitBtn.textContent = "Posting Review...";

    try {
      const response = await fetch(`/api/teachers/${teacherId}/reviews`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const result = await response.json();

      if (response.ok && result.success) {
        showAlert("success", "🎉 Thank you! Your anonymous review was published.");
        form.reset();
        setTimeout(() => {
          window.location.reload();
        }, 1200);
      } else {
        showAlert("error", `❌ ${result.error || "Could not post review."}`);
        submitBtn.disabled = false;
        submitBtn.textContent = "🚀 Submit Review";
      }
    } catch (err) {
      showAlert("error", "🌐 Server connection error. Please make sure the server is running!");
      submitBtn.disabled = false;
      submitBtn.textContent = "🚀 Submit Review";
    }
  });
}

// ==========================================================================
// 5. 👍 HELPFUL VOTE BUTTONS
// ==========================================================================
function setupVoteButtons() {
  const voteBtns = document.querySelectorAll(".btn-vote");

  voteBtns.forEach((btn) => {
    btn.addEventListener("click", async () => {
      const reviewId = btn.getAttribute("data-review-id");
      const voteVal = parseInt(btn.getAttribute("data-vote-val")); // 1 or -1

      btn.disabled = true;

      try {
        const response = await fetch(`/api/reviews/${reviewId}/vote`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ vote_value: voteVal })
        });
        const res = await response.json();
        if (response.ok && res.success) {
          const counter = btn.querySelector(".vote-count");
          if (counter) counter.textContent = res.new_count;
          btn.classList.add("voted");
        }
      } catch (e) {
        console.error("Voting error", e);
      } finally {
        btn.disabled = false;
      }
    });
  });
}

// ==========================================================================
// 6. 📢 UI ALERT HELPERS (Success & Error Messages)
// ==========================================================================
function showAlert(type, message) {
  clearAlerts();
  const alertContainer = document.getElementById("alert-container") || createAlertContainer();
  const alertBox = document.createElement("div");
  alertBox.className = `alert-box alert-${type}`;
  alertBox.textContent = message;
  alertContainer.appendChild(alertBox);

  alertBox.scrollIntoView({ behavior: "smooth", block: "center" });
}

function clearAlerts() {
  const container = document.getElementById("alert-container");
  if (container) container.innerHTML = "";
}

function createAlertContainer() {
  const container = document.createElement("div");
  container.id = "alert-container";
  container.style.margin = "1rem 0";
  const main = document.querySelector("main") || document.body;
  main.insertBefore(container, main.firstChild);
  return container;
}
