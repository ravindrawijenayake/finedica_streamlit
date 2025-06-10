<?php
session_start();

if (!isset($_SESSION['user_email'])) {
    header('Location: index.php');
    exit;
}

$userEmail = $_SESSION['user_email'];
$userName = $_SESSION['user_name'];

// Enable error reporting
error_reporting(E_ALL);
ini_set('display_errors', 1);

// Database connection
$host = 'localhost';
$dbname = 'user_reg_db'; // Use the user registration database
$username = 'root';
$password = '';

try {
    $pdo = new PDO("mysql:host=$host;port=3307;dbname=$dbname", $username, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
    die("Database connection failed: " . $e->getMessage());
}

// Check if user already has a record
$stmt = $pdo->prepare("SELECT responses, dominant_belief, money_resentment, financial_fantasists, money_prestige, money_anxiety FROM psychometric_test_responses WHERE email = :email LIMIT 1");
$stmt->execute([':email' => $userEmail]);
$existing = $stmt->fetch(PDO::FETCH_ASSOC);
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>20:20 FC - FINEDICA</title>
    <link rel="stylesheet" href="psychometric_test_style.css">
    <link rel="stylesheet" href="main.css">
    <link rel="stylesheet" href="../css/progressbar.css">
</head>
<body>
    <header>
        <nav class="navbar">
            <div class="logo">
                <h1>20:20 FC - FINEDICA</h1>
                <p>Expert Financial Coaching</p>
            </div>
            <ul>
                <li><a href="../php/index.php">Home</a></li>
                <li><a href="../php/questionnaire.php">Questionnaire</a></li>
                <li><a href="#contact">Contact</a></li>
                <li><a href="../generate_avatar/avatar_frontpage.php">Avatar</a></li>
                <li><a href="../chatbot/chatbot.php">Chatbot</a></li>
                <li><a href="../php/logout.php" style="font-size: 14px; color:rgb(7, 249, 168)">Logout <?php echo htmlspecialchars($userName); ?></a></li>
            </ul>
        </nav>  
    </header>
    <?php $progressStep = 1; include '../php/progressbar.php'; ?>
    <div class="container">
        <h1>Psychometric Money Belief Test Results</h1>
        <div id="already-submitted" style="display:none">
            <h2>🏆 Your Money Belief is </h2>
            <h3 id="prev-dominant"></h3>
            <h4>Category Scores</h4>
            <ul id="prev-scores"></ul>
            <h4>Your Responses</h4>
            <ul id="prev-answers"></ul>
            <div class="nav-buttons-row">
                <button id="back-btn" class="nav-btn nav-btn-left">Back</button>
                <button id="next-btn" class="nav-btn nav-btn-right">Next</button>
            </div>
        </div>
        <form id="psychometricForm" style="display:none">
            <div id="questionsContainer">
                <p> (1 = Strongly Disagree, 5 = Strongly Agree)</p>
                <!-- Questions will be dynamically loaded here -->
            </div>
            <button type="button" id="review-answers" style="margin-top: 20px;">Review Answers</button>
            <button type="submit" id="submit-btn" style="display:none;">Submit</button>
        </form>
        <div id="review-container" style="display: none; margin-top: 20px; padding: 10px; border: 1px solid #ccc; background-color: #f9f9f9;">
            <h3>Review Your Answers</h3>
            <div id="review-list"></div>
            <button id="edit-answers" style="margin-top:10px;">Edit Answers</button>
            <button id="final-submit" style="margin-top:10px;">Submit</button>
        </div>
        <div id="result" class="hidden">
            <h3 style="color: #2196f3; margin-top: 30px;">Your responses have been saved! You can view your results on your dashboard.</h3>
            <div class="nav-buttons-row">
                <button id="back-btn2" class="nav-btn nav-btn-left">Back</button>
                <button id="next-btn2" class="nav-btn nav-btn-right">Next</button>
            </div>
        </div>
    </div>
    <style>
        .nav-buttons-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 30px;
        }
        .nav-btn {
            padding: 12px 32px;
            font-size: 1.1em;
            border: none;
            border-radius: 6px;
            background: linear-gradient(90deg, #21f336 0%, #2196f3 100%);
            color: #fff;
            font-weight: bold;
            cursor: pointer;
            box-shadow: 0 2px 8px rgba(33,150,243,0.08);
            transition: background 0.2s, transform 0.2s;
        }
        .nav-btn-left {
            margin-right: auto;
        }
        .nav-btn-right {
            margin-left: auto;
        }
        .nav-btn:hover {
            background: linear-gradient(90deg, #2196f3 0%, #21f336 100%);
            transform: translateY(-2px) scale(1.04);
        }
        .highlight-missing {
            background: #ffeaea !important;
            border: 2px solid #e53935 !important;
        }
        .radio-group {
            display: flex;
            flex-direction: row;
            gap: 18px;
            margin: 8px 0 18px 0;
        }
        .radio-group label {
            display: flex;
            align-items: center;
            margin: 0;
        }
    </style>
    <script>
        // Define questions and categories as per psychometric_test.py
        const questionsByCategory = {
            "Money Resentment": [
                "If I have more money than most people in society, then, I do not deserve it.",
                "All rich people achieve wealth through greed and exploitation.",
                "I do not deserve to be wealthy.",
                "Caring about money makes you immoral.",
                "Rich people take advantage of others to earn their wealth."
            ],
            "Financial Fantasists": [
                "All problems  can be solved by spending money.",
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
        const descriptions = {
            "Money Resentment": "Money Resenters believe that money causes more problems in the world than it solves. This belief may be formed from some financial trauma in their past or family/social conditioning. They may believe that corporations control much of the world's economic power, and that ordinary people are exploited by capitalists. This manifests in behaviours that undermine their financial security. This could include giving away too much money, not investing, not educating themselves on financial products, never buying a house and not attempting to improve their earning capacity.that they do not deserve money. They may believe that wealthy people are greedy or corrupt. They often believe that there is virtue in living with less money.",
            "Financial Fantasists": "Financial Fantasists believe that money, and having more money, is the key to all life’s problems. Financial fantasists are never happy with what they have and always strive for more. If they have a problem, they look for something to buy or a service that may solve the issue. So, they will look for a coaching service instead of being introspective; they will think that they need a bigger house if someone they know has a bigger house. They are often jealous of people who have more money than they do and feel uncomfortable in their presence. Their dream is to be known for their wealth, and they would prefer their friends to have less money than they do.",
            "Money Prestige": "Money Status seekers believe that displays of wealth equate to their social standing. They are concerned with external validation, that someone notices the new car they are driving, the bag they have, or the watch they are wearing. These displays often come at the expense of their financial well-being and usually result in large amounts of debt and the mental health problems associated with toxic debt.",
            "Money Anxiety": "The Money Anxious are always fearful that they do not have enough money. They constantly worry about spending money on anything nice, struggle to treat themselves, and would prefer to buy second-hand items rather than invest in quality items that will last. This is usually the result of growing up in poverty. Even if they have money, they do not spend it. They are known as 'tight' or 'cheap.' They do not pay for professional services and often spend many hours and energy doing things themselves when they could afford to have someone else do it professionally."
        };
        const shortDescriptions = {
            "Money Resentment": "Believe money causes more problems in the world than it solves",
            "Financial Fantasists": "Believe money is the key to all life's problems",
            "Money Prestige": "Believe that displays of wealth equate to their social standing",
            "Money Anxiety": "Believe that if they do not have enough money, they should be fearful"
        };
        const answerMeanings = {
            1: 'Strongly Disagree',
            2: 'Disagree',
            3: 'Neutral',
            4: 'Agree',
            5: 'Strongly Agree'
        };
        let flatQuestions = [];
        let existing = <?php echo json_encode($existing ? $existing : null); ?>;
        document.addEventListener('DOMContentLoaded', function () {
            // Hide all sections initially
            document.getElementById('result').style.display = 'none';
            document.getElementById('already-submitted').style.display = 'none';
            document.getElementById('psychometricForm').style.display = 'none';

            if (existing) {
                // User has already submitted: show only previous results
                document.getElementById('already-submitted').style.display = '';
                document.getElementById('psychometricForm').style.display = 'none';
                document.getElementById('result').style.display = 'none';
                document.getElementById('prev-dominant').textContent = existing.dominant_belief;
                // Show full description for dominant belief
                const descDiv = document.createElement('div');
                descDiv.className = 'dominant-desc';
                descDiv.innerHTML = `<p style='margin-top:10px; font-size:1.1em; color:#333;'><b>Description:</b> ${descriptions[existing.dominant_belief]}</p>`;
                document.getElementById('prev-dominant').after(descDiv);
                const scoresList = document.getElementById('prev-scores');
                scoresList.innerHTML = '';
                scoresList.innerHTML += `<li>Money Resentment: ${existing.money_resentment}</li>`;
                scoresList.innerHTML += `<li>Financial Fantasists: ${existing.financial_fantasists}</li>`;
                scoresList.innerHTML += `<li>Money Prestige: ${existing.money_prestige}</li>`;
                scoresList.innerHTML += `<li>Money Anxiety: ${existing.money_anxiety}</li>`;
                // Answers (grouped by category)
                let ansList = document.getElementById('prev-answers');
                ansList.innerHTML = '';
                let prevAnswers = JSON.parse(existing.responses);
                let idx = 1;
                for (const cat of Object.keys(questionsByCategory)) {
                    ansList.innerHTML += `<li style='margin-top:10px;'><b>${cat}</b> <span style='color:#888;font-size:0.95em;'>(${shortDescriptions[cat]})</span></li>`;
                    for (let i=0; i<questionsByCategory[cat].length; i++) {
                        let val = prevAnswers[cat][i];
                        ansList.innerHTML += `<li style='margin-left:20px;'>${idx}. ${questionsByCategory[cat][i]}: <span style='color:#2196f3;'>${answerMeanings[val]||val||'No answer'}</span></li>`;
                        idx++;
                    }
                }
                document.getElementById('back-btn').onclick = ()=>window.history.back();
                document.getElementById('next-btn').onclick = ()=>window.location.href='../future_self/futureself.php';
                return;
            }

            // User has not submitted: show only the form
            document.getElementById('psychometricForm').style.display = '';
            document.getElementById('already-submitted').style.display = 'none';
            document.getElementById('result').style.display = 'none';
            const questionsContainer = document.getElementById('questionsContainer');
            flatQuestions = [];
            let qNum = 1;
            for (const [cat, qs] of Object.entries(questionsByCategory)) {
                // Add category title and short description
                const catDiv = document.createElement('div');
                catDiv.className = 'category-block';
                catDiv.innerHTML = `<h2 class='category-title'>${cat}</h2><p class='category-desc' style='color:#888;'>${shortDescriptions[cat]}</p>`;
                questionsContainer.appendChild(catDiv);
                for (const q of qs) {
                    flatQuestions.push({cat, q});
                    const questionDiv = document.createElement('div');
                    questionDiv.classList.add('question-item');
                    questionDiv.innerHTML = `
                        <label>${qNum}. ${q}</label>
                        <div class="radio-group">
                            <label><input type="radio" name="question_${qNum-1}" value="1" required> 1</label>
                            <label><input type="radio" name="question_${qNum-1}" value="2"> 2</label>
                            <label><input type="radio" name="question_${qNum-1}" value="3"> 3</label>
                            <label><input type="radio" name="question_${qNum-1}" value="4"> 4</label>
                            <label><input type="radio" name="question_${qNum-1}" value="5"> 5</label>
                        </div>
                    `;
                    questionsContainer.appendChild(questionDiv);
                    qNum++;
                }
            }
        });
        // Review answers before submission
        document.getElementById("review-answers").addEventListener("click", function () {
            const reviewContainer = document.getElementById("review-container");
            const reviewList = document.getElementById("review-list");
            reviewList.innerHTML = "";
            let allAnswered = true;
            // Group answers by category for review
            let qIdx = 0;
            for (const [cat, qs] of Object.entries(questionsByCategory)) {
                const catTitle = document.createElement('div');
                catTitle.innerHTML = `<h4 style='margin-top:18px; color:#2a5d84;'>${cat}</h4><p style='color:#888; margin-bottom:8px;'>${shortDescriptions[cat]}</p>`;
                reviewList.appendChild(catTitle);
                for (let i = 0; i < qs.length; i++) {
                    const val = document.querySelector(`input[name='question_${qIdx}']:checked`);
                    const qDiv = document.querySelectorAll('.question-item')[qIdx];
                    if (val) {
                        qDiv.classList.remove('highlight-missing');
                    } else {
                        qDiv.classList.add('highlight-missing');
                        allAnswered = false;
                    }
                    const reviewItem = document.createElement("div");
                    reviewItem.style.marginLeft = '18px';
                    reviewItem.style.marginBottom = '6px';
                    reviewItem.innerHTML = `<b>${qIdx+1}. ${qs[i]}</b>: <span style='color:#2196f3;'>${val ? answerMeanings[val.value] : 'No answer selected'}</span>`;
                    reviewList.appendChild(reviewItem);
                    qIdx++;
                }
            }
            if (!allAnswered) {
                alert('Please answer all questions before reviewing. Unanswered questions are highlighted.');
                const firstMissing = document.querySelector('.question-item.highlight-missing');
                if (firstMissing) firstMissing.scrollIntoView({behavior: 'smooth'});
                return;
            }
            reviewContainer.style.display = "block";
        });
        document.getElementById("edit-answers").addEventListener("click", function () {
            document.getElementById("review-container").style.display = "none";
        });
        document.getElementById("final-submit").addEventListener("click", function () {
            // Collect answers in the format: { category: [1,2,3,4,5], ... }
            const responses = {};
            let allAnswered = true;
            let qIndex = 0;
            for (const [category, qs] of Object.entries(questionsByCategory)) {
                responses[category] = [];
                for (let i = 0; i < qs.length; i++) {
                    const val = document.querySelector(`input[name='question_${qIndex}']:checked`);
                    const qDiv = document.querySelectorAll('.question-item')[qIndex];
                    if (!val) {
                        allAnswered = false;
                        qDiv.classList.add('highlight-missing');
                    } else {
                        qDiv.classList.remove('highlight-missing');
                    }
                    responses[category][i] = val ? parseInt(val.value) : null;
                    qIndex++;
                }
            }
            if (!allAnswered) {
                alert('Please answer all questions before submitting. Unanswered questions are highlighted.');
                const firstMissing = document.querySelector('.question-item.highlight-missing');
                if (firstMissing) firstMissing.scrollIntoView({behavior: 'smooth'});
                return;
            }
            fetch('save_psychometric_results.php', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ responses })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Instead of just showing a confirmation, reload the page to show the results section
                    window.location.reload();
                } else {
                    alert('Failed to save responses: ' + (data.error || 'Unknown error'));
                    document.getElementById('result').style.display = 'none';
                    document.getElementById('psychometricForm').style.display = '';
                    document.getElementById('already-submitted').style.display = 'none';
                }
            })
            .catch(err => {
                console.error('Error saving responses:', err);
                alert('An error occurred while saving your responses. Please try again.');
                document.getElementById('result').style.display = 'none';
                document.getElementById('psychometricForm').style.display = '';
                document.getElementById('already-submitted').style.display = 'none';
            });
        });
    </script>
</body>
</html>
