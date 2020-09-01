#/bin/sh
>&2 echo "16x16"
time openssl enc -aes-256-cbc -pass pass:123456 -salt -in images/lena_std_16_16.tif -out images/lena_std_16_16.enc
>&2 echo "32x32"
time openssl enc -aes-256-cbc -pass pass:123456 -salt -in images/lena_std_32_32.tif -out images/lena_std_32_32.enc
>&2 echo "64x64"
time openssl enc -aes-256-cbc -pass pass:123456 -salt -in images/lena_std_64_64.tif -out images/lena_std_64_64.enc
>&2 echo "128x128"
time openssl enc -aes-256-cbc -pass pass:123456 -salt -in images/lena_std_128_128.tif -out images/lena_std_128_128.enc
>&2 echo "256x256"
time openssl enc -aes-256-cbc -pass pass:123456 -salt -in images/lena_std_256_256.tif -out images/lena_std_256_256.enc
>&2 echo "512x512"
time openssl enc -aes-256-cbc -pass pass:123456 -salt -in images/lena_std_512_512.tif -out images/lena_std_512_512.enc
>&2 echo "1024x1024"
time openssl enc -aes-256-cbc -pass pass:123456 -salt -in images/lena_std_1024_1024.tif -out images/lena_std_1024_1024.enc
>&2 echo "2048x2048"
time openssl enc -aes-256-cbc -pass pass:123456 -salt -in images/lena_std_2048_2048.tif -out images/lena_std_2048_2048.enc
>&2 echo "4096x4096"
time openssl enc -aes-256-cbc -pass pass:123456 -salt -in images/lena_std_4096_4096.tif -out images/lena_std_4096_4096.enc
>&2 echo "Done!"
