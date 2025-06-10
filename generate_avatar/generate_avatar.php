<?php
// --- DEBUG LOGGING ---
file_put_contents(__DIR__ . '/avatar_debug.log', "Script started at " . date('c') . "\n", FILE_APPEND);
error_reporting(E_ALL);
ini_set('display_errors', 0); // Do not display errors to browser, only log

// --- OUTPUT BUFFER CLEANUP ---
if (ob_get_length()) ob_clean();

session_start();
file_put_contents(__DIR__ . '/avatar_debug.log', "After session_start at " . date('c') . "\n", FILE_APPEND);

require_once __DIR__ . '/db_config.php'; // Correct path for db_config.php

header('Content-Type: application/json');

// Only read php://input ONCE
$raw_input = file_get_contents('php://input');
file_put_contents('avatar_debug.log', json_encode(['post' => $_POST, 'input' => $raw_input, 'session' => $_SESSION, 'time' => date('c')]) . PHP_EOL, FILE_APPEND);

file_put_contents(__DIR__ . '/avatar_debug.log', "Request method: " . $_SERVER['REQUEST_METHOD'] . "\n", FILE_APPEND);

// Check if the request is valid
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    file_put_contents(__DIR__ . '/avatar_debug.log', "Not a POST request\n", FILE_APPEND);
    echo json_encode(['status' => 'error', 'message' => 'Invalid request method']);
    exit;
}

file_put_contents(__DIR__ . '/avatar_debug.log', "POST request received\n", FILE_APPEND);
file_put_contents(__DIR__ . '/avatar_debug.log', "Raw input: $raw_input\n", FILE_APPEND);
file_put_contents(__DIR__ . '/avatar_debug.log', "_POST: " . print_r($_POST, true) . "\n", FILE_APPEND);

// Get the user email from the request
$data = json_decode($raw_input, true);
file_put_contents(__DIR__ . '/avatar_debug.log', "POST data: " . var_export($data, true) . "\n", FILE_APPEND);
$email = $data['email'] ?? null;
file_put_contents(__DIR__ . '/avatar_debug.log', "Email after POST: $email\n", FILE_APPEND);

file_put_contents(__DIR__ . '/avatar_debug.log', "Email: $email\n", FILE_APPEND);
file_put_contents(__DIR__ . '/avatar_debug.log', "Session: " . print_r($_SESSION, true) . "\n", FILE_APPEND);

if (!$email) {
    file_put_contents(__DIR__ . '/avatar_debug.log', "No email provided\n", FILE_APPEND);
    echo json_encode(['status' => 'error', 'message' => 'Email is required']);
    exit;
}

// Get the selected stage from session (set by futureself.php)
if (!isset($_SESSION['submitted_stage'])) {
    $_SESSION['submitted_stage'] = 'General Financial Coaching'; // TEMP for testing
}
$stage = $_SESSION['submitted_stage'] ?? null;

file_put_contents(__DIR__ . '/avatar_debug.log', "Stage: $stage\n", FILE_APPEND);

if (!$stage) {
    file_put_contents(__DIR__ . '/avatar_debug.log', "No stage in session\n", FILE_APPEND);
    echo json_encode(['status' => 'error', 'message' => 'No stage found in session. Please complete the Future Self questionnaire.']);
    exit;
}

// Fetch user's gender from the users table
$user_gender = null;
try {
    // Use correct MySQL port 3307 (not 3306)
    $pdo = new PDO("mysql:host=localhost;port=3307;dbname=user_reg_db", 'root', '');
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $stmt = $pdo->prepare("SELECT gender FROM users WHERE email = :email LIMIT 1");
    $stmt->bindParam(':email', $email);
    $stmt->execute();
    $user_gender = $stmt->fetchColumn();
} catch (PDOException $e) {
    $user_gender = null;
}

// Map stage to prompt (refined for better avatar context)
$stage_prompts = [
    'Buying your first home' => 'A confident young adult, ready to buy their first home, smiling, standing in front of a modern house, professional avatar, photorealistic, modern house background',
    'Becoming a Parent' => 'A caring adult, soon to be a parent, gentle smile, holding a child or with a kid, warm background, professional avatar, photorealistic',
    'Planning Retirement' => 'A wise adult planning for retirement, thoughtful expression, relaxing in a garden or with travel elements, calm background, professional avatar, photorealistic',
    'Retirement' => 'A happy retiree, relaxed and content, with family or in a serene setting, peaceful background, professional avatar, photorealistic',
    'General Financial Coaching' => 'A professional, approachable person, ready for financial coaching, office or neutral background, professional avatar, photorealistic',
];
$prompt = $stage_prompts[$stage] ?? $stage_prompts['General Financial Coaching'];

// Add gender to prompt if available
if ($user_gender) {
    $prompt = ($user_gender === 'Male' ? 'A man. ' : ($user_gender === 'Female' ? 'A woman. ' : '')) . $prompt;
}

file_put_contents(__DIR__ . '/avatar_debug.log', "Prompt: $prompt\n", FILE_APPEND);

// Extract Physicality responses for dynamic prompt
$physicality_desc = '';
if (isset($_SESSION['submitted_responses']['Physicality'])) {
    $phys = $_SESSION['submitted_responses']['Physicality'];
    foreach ($phys as $q => $a) {
        $physicality_desc .= ' ' . $a . '.';
    }
}
if (trim($physicality_desc)) {
    $prompt .= ' ' . trim($physicality_desc);
}
file_put_contents(__DIR__ . '/avatar_debug.log', "Final Prompt: $prompt\n", FILE_APPEND);

// === Stability AI Avatar Generation ===
$stability_api_key = 'sk-hV3rJIrVaxzsLiq0FwEQ9RNCYBwvm1NcMXwkYhfpUuABSnds'; // <-- Replace with your Stability AI key
$stability_url = 'https://api.stability.ai/v2beta/stable-image/generate/core';

// Get the uploaded face image path for the user
$face_image_path = null;
try {
    $pdo = new PDO("mysql:host=localhost;port=3307;dbname=user_reg_db", 'root', '');
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $stmt = $pdo->prepare("SELECT face_image_url FROM face_image_responses WHERE email = :email ORDER BY id DESC LIMIT 1");
    $stmt->bindParam(':email', $email);
    $stmt->execute();
    $face_image_path = $stmt->fetchColumn();
} catch (PDOException $e) {
    echo json_encode(['status' => 'error', 'message' => 'DB error: ' . $e->getMessage()]);
    exit;
}

// Check that the face image file exists and is not empty
if (!$face_image_path || !file_exists($face_image_path) || filesize($face_image_path) === 0) {
    file_put_contents(__DIR__ . '/avatar_debug.log', "No valid uploaded face image found for this user.\n", FILE_APPEND);
    echo json_encode(['status' => 'error', 'message' => 'No valid uploaded face image found for this user.']);
    exit;
}

$avatar_filename = 'avatar_' . preg_replace('/[^a-zA-Z0-9_\.\@-]/', '', $email) . '.png';
$avatar_path = __DIR__ . '/../avatars/' . $avatar_filename;

// Prepare multipart form data for Stability AI (with image and prompt)
$boundary = uniqid();
$delimiter = '-------------' . $boundary;
$postData = "--$delimiter\r\n";
$postData .= "Content-Disposition: form-data; name=\"prompt\"\r\n\r\n";
$postData .= $prompt . "\r\n";
$postData .= "--$delimiter\r\n";
$postData .= "Content-Disposition: form-data; name=\"image\"; filename=\"face.png\"\r\n";
$postData .= "Content-Type: image/png\r\n\r\n";
$postData .= file_get_contents($face_image_path) . "\r\n";
$postData .= "--$delimiter\r\n";
$postData .= "Content-Disposition: form-data; name=\"output_format\"\r\n\r\n";
$postData .= "png\r\n";
$postData .= "--$delimiter--\r\n";

$ch = curl_init($stability_url);
curl_setopt_array($ch, [
    CURLOPT_POST => true,
    CURLOPT_POSTFIELDS => $postData,
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_HTTPHEADER => [
        'Authorization: Bearer ' . $stability_api_key,
        "Content-Type: multipart/form-data; boundary=$delimiter",
        "Accept: image/*"
    ],
]);
$response = curl_exec($ch);
$http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$err = curl_error($ch);
$curl_info = curl_getinfo($ch);
curl_close($ch);

// Log the full response and cURL info for debugging
file_put_contents(__DIR__ . '/avatar_debug.log', "[curl_info] => " . print_r($curl_info, true) . "\n", FILE_APPEND);
file_put_contents(__DIR__ . '/avatar_debug.log', "[http_code] => $http_code\n", FILE_APPEND);
file_put_contents(__DIR__ . '/avatar_debug.log', "[curl_error] => $err\n", FILE_APPEND);
file_put_contents(__DIR__ . '/avatar_debug.log', "[api_response] => $response\n", FILE_APPEND);

if ($http_code === 200 && $response) {
    // Save the avatar image to the avatars folder
    $save_result = file_put_contents($avatar_path, $response);
    file_put_contents(__DIR__ . '/avatar_debug.log', "[avatar_path] => $avatar_path\n[save_result] => $save_result\n", FILE_APPEND);
    if ($save_result === false) {
        echo json_encode(['status' => 'error', 'message' => 'Failed to save avatar image to avatars folder.']);
        exit;
    }

    // Save the avatar path to the database
    $conn = getDatabaseConnection();
    if (!$conn) {
        file_put_contents(__DIR__ . '/avatar_debug.log', "[db_error] => Failed to connect to database\n", FILE_APPEND);
        echo json_encode(['status' => 'error', 'message' => 'Failed to connect to database.']);
        exit;
    }
    $stmt = $conn->prepare('INSERT INTO avatars (email, image_path) VALUES (?, ?) ON DUPLICATE KEY UPDATE image_path = VALUES(image_path)');
    if (!$stmt) {
        file_put_contents(__DIR__ . '/avatar_debug.log', "[db_error] => Prepare failed: " . $conn->error . "\n", FILE_APPEND);
        echo json_encode(['status' => 'error', 'message' => 'Failed to prepare database statement.']);
        $conn->close();
        exit;
    }
    $stmt->bind_param('ss', $email, $avatar_filename);
    $exec_result = $stmt->execute();
    file_put_contents(__DIR__ . '/avatar_debug.log', "[db_exec_result] => $exec_result\n[db_error] => " . $stmt->error . "\n", FILE_APPEND);
    if (!$exec_result) {
        echo json_encode(['status' => 'error', 'message' => 'Failed to save avatar path to database.']);
        $stmt->close();
        $conn->close();
        exit;
    }
    $stmt->close();
    $conn->close();
    $web_path = "/2020FC/src/avatars/" . $avatar_filename;
    echo json_encode(['status' => 'ok', 'avatar_path' => $web_path]);
    exit;
} else {
    // Try to decode JSON error from API
    $api_error = @json_decode($response, true);
    $api_error_msg = $api_error['error']['message'] ?? $response;
    echo json_encode(['status' => 'error', 'message' => 'Avatar generation failed (Stability AI): ' . $api_error_msg]);
    exit;
}
?>