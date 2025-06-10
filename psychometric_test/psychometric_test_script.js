// psychometric_test_script.js

document.addEventListener('DOMContentLoaded', function () {
    fetch('http://localhost:5002/get_questions', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(res => res.json())
    .then(data => {
        const questionsContainer = document.getElementById('questionsContainer');
        data.questions.forEach((question, index) => {
            const questionDiv = document.createElement('div');
            questionDiv.classList.add('question');
            questionDiv.innerHTML = `
                <p>${index + 1}. ${question.text}</p>
                <label><input type="radio" name="question_${index}" value="1" required> 1</label>
                <label><input type="radio" name="question_${index}" value="2"> 2</label>
                <label><input type="radio" name="question_${index}" value="3"> 3</label>
                <label><input type="radio" name="question_${index}" value="4"> 4</label>
                <label><input type="radio" name="question_${index}" value="5"> 5</label>
            `;
            questionsContainer.appendChild(questionDiv);
        });
    })
    .catch(err => {
        console.error('Error fetching questions:', err);
        alert('Failed to load questions. Please try again later.');
    });
});

const questions = {
    "Money Resentment": [
        "If I have more money than most people in society, then, I do not deserve it.",
        "All rich people achieve wealth through greed and exploitation.",
        "I do not deserve to be wealthy.",
        "Caring about money makes you immoral.",
        "Rich people take advantage of others to earn their wealth."
    ],
    "Financial Fantasists": [
        "All problems can be solved by spending money.",
        "You cannot be happy unless you are rich.",
        "People who are happy must be unhappy.",
        "You should always seek to have more money.",
        "Money is a way of gaining power and influence."
    ],
    "Money Prestige": [
        "I am what I own.",
        "I need to keep up with the Joneses.",
        "When I have nice things, I have more self-esteem",
        "People with more money are more important than people with less money.",
        "Money makes your life more appealing."
    ],
    "Money Anxiety": [
        "Never pay for something you can do yourself.",
        "Money should be saved at all costs.",
        "I do not spend money when I don't have to pay.",
        "Paying for luxury is a waste.",
        "You should always keep as much money as possible for an emergency."
    ]
};

document.addEventListener("DOMContentLoaded", function () {
    const container = document.getElementById("questionnaire");
    const reviewContainer = document.getElementById("review-container");
    const submitButton = document.getElementById("submit-test");
    const reviewButton = document.getElementById("review-answers");

    // Populate questions
    for (let category in questions) {
        const catTitle = document.createElement("h2");
        catTitle.className = "category-title";
        catTitle.textContent = category;
        container.appendChild(catTitle);

        questions[category].forEach((question, index) => {
            const div = document.createElement("div");
            div.className = "question";

            const label = document.createElement("label");
            label.textContent = question;

            const select = document.createElement("select");
            select.name = `${category}_${index}`;
            for (let i = 1; i <= 5; i++) {
                const option = document.createElement("option");
                option.value = i;
                option.textContent = `${i} - ${[
                    "Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"
                ][i - 1]}`;
                select.appendChild(option);
            }

            div.appendChild(label);
            div.appendChild(select);
            container.appendChild(div);
        });
    }

    // Review answers before submission
    reviewButton.addEventListener("click", function () {
        const selects = document.querySelectorAll("select");
        reviewContainer.innerHTML = ""; // Clear previous review

        selects.forEach(select => {
            const [category, index] = select.name.split("_");
            const questionText = questions[category][index];
            const selectedValue = select.value;

            const reviewItem = document.createElement("p");
            if (selectedValue) {
                reviewItem.textContent = `${questionText}: ${selectedValue}`;
            } else {
                reviewItem.textContent = `${questionText}: No answer selected`;
            }
            reviewContainer.appendChild(reviewItem);
        });

        reviewContainer.style.display = "block"; // Show the review container
    });

    // Submit answers
    submitButton.addEventListener("click", function (e) {
        e.preventDefault();
        // Highlight unanswered questions
        let hasMissing = false;
        document.querySelectorAll('.question').forEach(div => {
            const checked = div.querySelector('input[type="radio"]:checked');
            if (!checked) {
                div.style.background = '#ffeaea'; // light red
                div.style.border = '2px solid #e53935';
                hasMissing = true;
            } else {
                div.style.background = '';
                div.style.border = '';
            }
        });
        if (hasMissing) {
            alert('Please answer all questions. Unanswered questions are highlighted.');
            // Optionally scroll to first missing
            const firstMissing = document.querySelector('.question[style*="e53935"]');
            if (firstMissing) firstMissing.scrollIntoView({behavior: 'smooth'});
            return;
        }

        const selects = document.querySelectorAll("input[type='radio']:checked");
        const responses = {};

        selects.forEach(select => {
            const [category, index] = select.name.split("_");
            if (!responses[category]) responses[category] = {};
            responses[category][index] = parseInt(select.value) || null; // Handle unselected values
        });

        // Validate responses
        const totalQuestions = document.querySelectorAll("input[type='radio']").length / 5; // Assuming 5 options per question
        if (Object.keys(responses).length !== totalQuestions) {
            alert("Please answer all questions before submitting.");
            return;
        }

        // Debugging log
        console.log("Submitting data:", responses);

        // Send data to the backend
        fetch('save_psychometric_results.php', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ responses })
        })
        .then(response => response.json())
        .then(data => {
            console.log("Response from backend:", data); // Debugging log
            if (data.success) {
                alert("Your responses have been saved successfully!");
            } else {
                alert("Failed to save responses: " + (data.error || "Unknown error"));
            }
        })
        .catch(err => {
            console.error("Error saving responses:", err);
            alert("An error occurred while saving your responses. Please try again.");
        });
    });
});
