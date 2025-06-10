<?php
$result = file_put_contents(__DIR__ . '/../avatars/test_write.png', 'test');
if ($result === false) {
    echo "FAILED: Cannot write to avatars folder!";
} else {
    echo "SUCCESS: Can write to avatars folder!";
}
?>