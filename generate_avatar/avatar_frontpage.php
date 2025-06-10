<?php
session_start();

// Check login
if (!isset($_SESSION['user_email'])) {
    header('Location: index.php');
    exit;
}

$userEmail = $_SESSION['user_email'];
$userName = $_SESSION['user_name'];

// Database connection
$host = 'localhost';
$dbname = 'user_reg_db';
$username = 'root';
$password = 'finedica';

try {
    $pdo = new PDO("mysql:host=$host;port=3307;dbname=$dbname", $username, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    $stmt = $pdo->prepare("SELECT face_image_url FROM face_image_responses WHERE email = :email ORDER BY id DESC LIMIT 1");
    $stmt->bindParam(':email', $userEmail);
    $stmt->execute();
    $faceImageUrl = $stmt->fetchColumn();
} catch (PDOException $e) {
    die("Database connection failed: " . $e->getMessage());
}

// Check if avatar exists for this user and get its path
$avatarPath = null;
try {
    $stmt = $pdo->prepare("SELECT image_path FROM avatars WHERE email = :email LIMIT 1");
    $stmt->bindParam(':email', $userEmail);
    $stmt->execute();
    $avatarPath = $stmt->fetchColumn();
} catch (PDOException $e) {
    $avatarPath = null;
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Review Your Face Image</title>
    <link rel="stylesheet" href="../css/main.css">
    <link rel="stylesheet" href="../generate_avatar/avatarstyle.css">
    <link rel="stylesheet" href="../css/progressbar.css">
    <link rel="stylesheet" href="../css/futureselfstyle.css">
    <script>
        const userEmail = "<?php echo $userEmail; ?>";
    </script>
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
                <li><a href="avatar.php">Avatar</a></li>
                <li><a href="../chatbot/chatbot.php">Chatbot</a></li>
                <li><a href="../php/logout.php">Logout <?php echo htmlspecialchars($userName); ?></a></li>
            </ul>
        </nav>
    </header>
    <?php $progressStep = 4; include '../php/progressbar.php'; ?>
    <main>
        <div class="futureself-hero" style="display: flex; justify-content: center; align-items: center;">
            <h1 style="text-align: center;"><span class="icon">🧑‍🎨</span> Your Personalised Avatar</h1>
        </div>
        <div class="futureself-avatar-card card" style="max-width: 400px; margin: 32px auto; text-align: center; padding: 32px 24px;">
            <?php if ($avatarPath): ?>
                <img src="/finedica/avatars/<?php echo htmlspecialchars($avatarPath); ?>?t=<?php echo time(); ?>"
                     alt="Generated Avatar"
                     style="max-width: 250px; max-height: 250px; border-radius: 18px; box-shadow: 0 4px 24px rgba(33,150,243,0.18); border: 3px solid #2196f3; background: #f8f8f8; margin-bottom: 24px; display: block; margin-left: auto; margin-right: auto;" />
                <button id="regenerate-avatar-btn" class="futureself-btn" style="margin-top: 18px;">Re-generate Avatar</button>
                <p class="avatar-info-text" style="margin-top: 18px; color: #666; font-size: 1.05em;">Not happy with your avatar? Click above to try again!</p>
            <?php else: ?>
                <p class="avatar-info-text">No avatar generated yet.</p>
            <?php endif; ?>
        </div>
    </main>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const regenBtn = document.getElementById('regenerate-avatar-btn');
            if (regenBtn) {
                regenBtn.onclick = function() {
                    if (confirm('To re-generate your avatar, you must re-upload your face image and re-take the Future Self test. Do you want to proceed?')) {
                        if (confirm('This will delete your previous avatar and responses. Do you consent to proceed?')) {
                            window.location.href = '../future_self/face_image.php?reupload=1';
                        }
                    }
                };
            }
        });
    </script>
</body>
</html>
