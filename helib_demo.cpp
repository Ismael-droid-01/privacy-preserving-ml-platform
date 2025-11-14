#include <helib/helib.h>
#include <iostream>
#include <vector>
#include <chrono>

int main() {
    // Parámetros del contexto CKKS
    unsigned long m = 16384;  // índice ciclotómico
    unsigned long bits = 300; // tamaño de los bits de seguridad
    unsigned long c = 2;      // columnas de llaves
    unsigned long precision = 40; // precisión en bits para CKKS

    std::cout << "Inicializando contexto..." << std::endl;
    auto context = helib::ContextBuilder<helib::CKKS>()
                       .m(m)
                       .bits(bits)
                       .precision(precision)
                       .c(c)
                       .build();

    // Generación de llaves
    helib::SecKey secretKey(context);
    secretKey.GenSecKey();
    const helib::PubKey& publicKey = secretKey;

    // Datos de entrada
    std::vector<double> x = {5.3, 2.7};
    std::vector<double> y = {1.5, 3.2};

    // Cifrado
    helib::Ptxt<helib::CKKS> ptxt1(context, x);
    helib::Ptxt<helib::CKKS> ptxt2(context, y);
    helib::Ctxt ctxt1(publicKey);
    helib::Ctxt ctxt2(publicKey);
    publicKey.Encrypt(ctxt1, ptxt1);
    publicKey.Encrypt(ctxt2, ptxt2);

    // Ciclo de operaciones para medir rendimiento
    int iters = 1000;
    std::cout << "Ejecutando " << iters << " operaciones homomórficas...\n";

    auto start_sum = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < iters; i++) {
        helib::Ctxt tmp = ctxt1;
        tmp += ctxt2;
    }
    auto end_sum = std::chrono::high_resolution_clock::now();

    auto start_mul = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < iters; i++) {
        helib::Ctxt tmp = ctxt1;
        tmp *= ctxt2;
    }
    auto end_mul = std::chrono::high_resolution_clock::now();

    double sum_time = std::chrono::duration<double>(end_sum - start_sum).count();
    double mul_time = std::chrono::duration<double>(end_mul - start_mul).count();

    std::cout << "Tiempo total (sumas): " << sum_time << " s\n";
    std::cout << "Tiempo total (multiplicaciones): " << mul_time << " s\n";
    std::cout << "Promedio por suma: " << sum_time / iters << " s\n";
    std::cout << "Promedio por multiplicación: " << mul_time / iters << " s\n";

    // Desencriptar resultados
    helib::Ctxt ctxt_sum = ctxt1;
    ctxt_sum += ctxt2;

    helib::Ctxt ctxt_prod = ctxt1;
    ctxt_prod *= ctxt2;

    helib::Ptxt<helib::CKKS> dec_sum(context);
    helib::Ptxt<helib::CKKS> dec_prod(context);

    secretKey.Decrypt(dec_sum, ctxt_sum);
    secretKey.Decrypt(dec_prod, ctxt_prod);

    std::cout << "Suma desencriptada: ";
    for (size_t i = 0; i < dec_sum.size(); ++i)
        std::cout << dec_sum[i] << " ";
    std::cout << "\n";

    std::cout << "Producto desencriptado: ";
    for (size_t i = 0; i < dec_prod.size(); ++i)
        std::cout << dec_prod[i] << " ";
    std::cout << "\n";

    return 0;
}
