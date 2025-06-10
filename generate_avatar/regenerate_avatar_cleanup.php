<?php
// regenerate_avatar_cleanup.php
header('Content-Type: application/json');
session_start();

$data = json_decode(file_get_contents('php://input'), true);
$email = $data['email'] ?? $_SESSION['user_email'] ?? null;

if (!$email) {
    echo json_encode(['status' => 'error', 'message' => 'No email provided.']);
    exit;
}

$host = 'localhost';
$dbname = 'user_reg_db';
$username = 'root';
$password = 'finedica';

try {
    $pdo = new PDO("mysql:host=$host;port=3307;dbname=$dbname", $username, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    // Delete avatar record and file
    $stmt = $pdo->prepare("SELECT image_path FROM avatars WHERE email = :email LIMIT 1");
    $stmt->bindParam(':email', $email);
    $stmt->execute();
    $avatarPath = $stmt->fetchColumn();
    if ($avatarPath) {
        // Try both absolute and relative path for avatar file deletion
        $avatarFileAbs = realpath(__DIR__ . '/../avatars/' . basename($avatarPath));
        $avatarFileRel = __DIR__ . '/../avatars/' . basename($avatarPath);
        if ($avatarFileAbs && file_exists($avatarFileAbs)) {
            @unlink($avatarFileAbs);
        } elseif (file_exists($avatarFileRel)) {
            @unlink($avatarFileRel);
        }
        $pdo->prepare("DELETE FROM avatars WHERE email = :email")->execute([':email' => $email]);
    }

    // Delete future self responses
    $pdo->prepare("DELETE FROM future_self_responses WHERE email = :email")->execute([':email' => $email]);

    // Optionally clear session data
    unset($_SESSION['submitted_stage'], $_SESSION['submitted_responses']);

    echo json_encode(['status' => 'ok']);
    exit;
} catch (PDOException $e) {
    echo json_encode(['status' => 'error', 'message' => 'DB error: ' . $e->getMessage()]);
    exit;
}
