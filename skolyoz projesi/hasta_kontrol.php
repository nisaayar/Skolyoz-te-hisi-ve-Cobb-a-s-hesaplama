<?php
// Veritabanı bağlantısı
$servername = "localhost"; // Veritabanı sunucusu
$username = "root"; // Veritabanı kullanıcı adı
$password = "nisa2002"; // Veritabanı şifresi
$dbname = "skolyoz_teshis_sistemi"; // Veritabanı adı

$conn = new mysqli($servername, $username, $password, $dbname);

// Bağlantı kontrolü
if ($conn->connect_error) {
    die("Bağlantı başarısız: " . $conn->connect_error);
}

// Formdan gelen hasta adını al ve temizle
$hasta_adi = isset($_POST['hasta_adi']) ? trim($_POST['hasta_adi']) : '';

// Hasta kontrolü
$sql = "SELECT * FROM hastalar WHERE ad = ?";
$stmt = $conn->prepare($sql);
$stmt->bind_param("s", $hasta_adi);
$stmt->execute();
$result = $stmt->get_result();

if ($result->num_rows > 0) {
    // Hasta bulundu, bilgileri göster
    $hasta = $result->fetch_assoc();
    // Hasta bilgilerini URL parametreleriyle geçebilirsiniz
    header("Location: hasta_git.html?hasta_id=" . $hasta['hasta_id']);
    exit; // Yönlendirme sonrası scriptin devam etmemesi için exit ekliyoruz
} else {
    // Hasta bulunamadı
    echo "<script>alert('Üzgünüm, böyle bir hasta yoktur.'); window.history.back();</script>";
}

$stmt->close();
$conn->close();