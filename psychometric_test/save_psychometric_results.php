<?php
session_start();
header("Content-Type: application/json");

// Database connection
$host = 'localhost';
$dbname = 'user_reg_db';
$username = 'root';
$password = '';

try {
    $pdo = new PDO("mysql:host=$host;port=3307;dbname=$dbname", $username, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
    echo json_encode(["success" => false, "error" => "Database connection failed: " . $e->getMessage()]);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $data = json_decode(file_get_contents("php://input"), true);
    $email = $_SESSION['user_email'] ?? null;
    $responses = $data['responses'] ?? null;

    // Debugging logs
    error_log("Received email: " . $email);
    error_log("Received responses: " . print_r($responses, true));

    if (!$email || !$responses) {
        echo json_encode(["success" => false, "error" => "Missing email or responses."]);
        exit;
    }

    // Calculate scores for each category
    $category_scores = [];
    foreach ($responses as $category => $answers) {
        $category_scores[$category] = array_sum($answers);
    }

    // Find dominant belief
    $dominant_belief = array_keys($category_scores, max($category_scores))[0];

    try {
        $stmt = $pdo->prepare("INSERT INTO psychometric_test_responses 
            (email, dominant_belief, money_resentment, financial_fantasists, money_prestige, money_anxiety, responses)
            VALUES (:email, :dominant_belief, :money_resentment, :financial_fantasists, :money_prestige, :money_anxiety, :responses)
            ON DUPLICATE KEY UPDATE
                dominant_belief = VALUES(dominant_belief),
                money_resentment = VALUES(money_resentment),
                financial_fantasists = VALUES(financial_fantasists),
                money_prestige = VALUES(money_prestige),
                money_anxiety = VALUES(money_anxiety),
                responses = VALUES(responses),
                updated_at = CURRENT_TIMESTAMP");

        $stmt->execute([
            ':email' => $email,
            ':dominant_belief' => $dominant_belief,
            ':money_resentment' => $category_scores['Money Resentment'] ?? 0,
            ':financial_fantasists' => $category_scores['Financial Fantasists'] ?? 0,
            ':money_prestige' => $category_scores['Money Prestige'] ?? 0,
            ':money_anxiety' => $category_scores['Money Anxiety'] ?? 0,
            ':responses' => json_encode($responses)
        ]);

        echo json_encode([
            'success' => true,
            'scores' => $category_scores,
            'dominant_belief' => $dominant_belief
        ]);
    } catch (PDOException $e) {
        echo json_encode(["success" => false, "error" => $e->getMessage()]);
    }
    exit;
}
?>
