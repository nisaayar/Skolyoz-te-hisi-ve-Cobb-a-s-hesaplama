<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Skolyoz Analizi</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 flex items-center justify-center h-screen">
    <div class="bg-white p-6 rounded-lg shadow-lg w-96">
        <h1 class="text-lg font-bold mb-4">Skolyoz Analizi</h1>
        
        <?php
        // URL parametrelerini al
        $isim = isset($_GET['isim']) ? htmlspecialchars($_GET['isim']) : 'Bilinmiyor';
        $soyisim = isset($_GET['soyisim']) ? htmlspecialchars($_GET['soyisim']) : 'Bilinmiyor';
        $cinsiyet = isset($_GET['cinsiyet']) ? htmlspecialchars($_GET['cinsiyet']) : 'Bilinmiyor';
        $dogumTarihi = isset($_GET['dogumTarihi']) ? htmlspecialchars($_GET['dogumTarihi']) : 'Bilinmiyor';
        $digerBilgiler = isset($_GET['digerBilgiler']) ? htmlspecialchars($_GET['digerBilgiler']) : 'Bilinmiyor';

        // Bilgileri göster
        $bilgiler = [
            'İsim' => $isim,
            'Soyisim' => $soyisim,
            'Cinsiyet' => $cinsiyet,
            'Doğum Tarihi' => $dogumTarihi,
            'Diğer Bilgiler' => $digerBilgiler
        ];

        foreach ($bilgiler as $label => $value) {
            echo "<div class='mb-4'><strong>$label:</strong> <span class='text-gray-700'>$value</span></div>";
        }
        ?>

        <div class="flex justify-center">
            <a href="javascript:history.back()">
                <button class="bg-gray-300 text-black py-2 px-4 rounded hover:bg-gray-400 transition">
                    Geri
                </button>
            </a>
        </div>
    </div>
</body>
</html>