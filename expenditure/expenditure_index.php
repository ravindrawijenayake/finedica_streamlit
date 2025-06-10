<?php
session_start();

if (!isset($_SESSION['user_id'])) {
    header('Location: index.php');
    exit;
}

$userName = $_SESSION['user_name'];
?>



<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>20:20 FC - FINEDICA</title>
    <link rel="stylesheet" href="../css/main.css">
    <link rel="stylesheet" href="../css/expenditurestyle.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <header>
        <nav class="navbar">
            <div class="logo">
                <h1>20:20 FC - FINEDICA</h1>
                <p>Expert Financial Coaching</p>
            </div>
            <ul>
                <li><a href="../php/home.php">Home</a></li>
                <li><a href="../php/questionnaire.php">Questionnaire</a></li>
                <li><a href="#contact">Contact</a></li>
                <li><a href="../php/avatar_frontpage.php">Avatar</a></li>
                <li><a href="../php/chatbot.php">Chatbot</a></li>
                <li><a href="../php/logout.php" style="font-size: 14px; color:rgb(7, 249, 168)">Logout <?php echo htmlspecialchars($userName);?></a></li>
            </ul>
        </nav>  
    </header>
    <main class="expenditure-main">
        <section class="expenditure-hero">
            <h1>Monthly Income & Expenditure Tracker</h1>
            <p class="expenditure-subtitle">Easily track, visualize, and optimize your monthly budget. Enter your details below and get instant insights!</p>
        </section>
        <div class="expenditure-flex-container">
            <form id="budgetForm" class="expenditure-form card">
                <h2>Income</h2>
                <div class="section">
                    <label>Salary: <input type="number" name="salary" placeholder="Net Monthly Salary" /></label>
                    <label>Dividends: <input type="number" name="dividends" /></label>
                    <label>State Pension: <input type="number" name="statePension" /></label>
                    <label>Pension: <input type="number" name="pension" /></label>
                    <label>Benefits: <input type="number" name="benefits" /></label>
                    <label>Other: <input type="number" name="otherIncome" /></label>
                </div>
                <h2>Home Expenses</h2>
                <div class="section">
                    <label>Gas: <input type="number" name="gas" /></label>
                    <label>Electric: <input type="number" name="electric" /></label>
                    <label>Water: <input type="number" name="water" /></label>
                    <label>Council Tax: <input type="number" name="councilTax" /></label>
                    <label>Phone: <input type="number" name="phone" /></label>
                    <label>Internet: <input type="number" name="internet" /></label>
                    <label>Mobile: <input type="number" name="mobilePhone" /></label>
                    <label>Food: <input type="number" name="food" /></label>
                    <label>Others: <input type="number" name="otherHome" /></label>
                </div>
                <h2>Travel Expenses</h2>
                <div class="section">
                    <label>Petrol: <input type="number" name="petrol" /></label>
                    <label>Car Tax: <input type="number" name="carTax" /></label>
                    <label>Insurance: <input type="number" name="carInsurance" /></label>
                    <label>Maintenance: <input type="number" name="maintenance" /></label>
                    <label>Public Transport: <input type="number" name="publicTransport" /></label>
                    <label>Others: <input type="number" name="otherTravel" /></label>
                </div>
                <!-- Add similar sections for Miscellaneous, Children, Insurance, Pay Slip Deductions -->
                <button type="submit" class="expenditure-submit-btn">Calculate</button>
            </form>
            <div class="expenditure-results-panel card">
                <div id="results"></div>
                <canvas id="expenseChart" width="340" height="340" style="max-width:340px; margin: 0 auto; display: block;"></canvas>
            </div>
        </div>
    </main>
    <script src="expenditure_script.js"></script>
</body>
</html>
