#include <seal/seal.h>
#include <iostream>
#include <vector>
#include <chrono>

int main() {
    // Parámetros del contexto CKKS
    size_t poly_modulus_degree = 8192;   // grado del polinomio (8192 recomendado)
    seal::EncryptionParameters parms(seal::scheme_type::ckks);
    parms.set_poly_modulus_degree(poly_modulus_degree);

    // coeficiente del módulo (niveles de ruido)
    parms.set_coeff_modulus(seal::CoeffModulus::Create(
        poly_modulus_degree, {60, 40, 40, 60}
    ));

    std::cout << "Inicializando contexto..." << std::endl;
    seal::SEALContext context(parms);

    // Generación de llaves
    seal::KeyGenerator keygen(context);

    seal::PublicKey publicKey;
    keygen.create_public_key(publicKey);

    seal::SecretKey secretKey = keygen.secret_key();

    seal::RelinKeys relinKeys;
    keygen.create_relin_keys(relinKeys);

    seal::Encryptor encryptor(context, publicKey);
    seal::Evaluator evaluator(context);
    seal::Decryptor decryptor(context, secretKey);
    seal::CKKSEncoder encoder(context);

    double scale = pow(2.0, 40);

    // Datos de entrada
    std::vector<double> x = {5.3, 2.7};
    std::vector<double> y = {1.5, 3.2};

    // Codificación
    seal::Plaintext ptxt1, ptxt2;
    encoder.encode(x, scale, ptxt1);
    encoder.encode(y, scale, ptxt2);

    // Cifrado
    seal::Ciphertext ctxt1, ctxt2;
    encryptor.encrypt(ptxt1, ctxt1);
    encryptor.encrypt(ptxt2, ctxt2);

    // Ciclo de operaciones para medir rendimiento
    int iters = 1000;
    std::cout << "Ejecutando " << iters << " operaciones homomórficas...\n";

    auto start_sum = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < iters; i++) {
        seal::Ciphertext tmp = ctxt1;
        evaluator.add_inplace(tmp, ctxt2);
    }
    auto end_sum = std::chrono::high_resolution_clock::now();

    auto start_mul = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < iters; i++) {
        seal::Ciphertext tmp = ctxt1;
        evaluator.multiply_inplace(tmp, ctxt2);
        evaluator.relinearize_inplace(tmp, relinKeys);
        evaluator.rescale_to_next_inplace(tmp);   // CKKS necesita rescale
    }
    auto end_mul = std::chrono::high_resolution_clock::now();

    double sum_time = std::chrono::duration<double>(end_sum - start_sum).count();
    double mul_time = std::chrono::duration<double>(end_mul - start_mul).count();

    std::cout << "Tiempo total (sumas): " << sum_time << " s\n";
    std::cout << "Tiempo total (multiplicaciones): " << mul_time << " s\n";
    std::cout << "Promedio por suma: " << sum_time / iters << " s\n";
    std::cout << "Promedio por multiplicación: " << mul_time / iters << " s\n";

    // Desencriptar resultados
    seal::Ciphertext ctxt_sum, ctxt_prod;
    evaluator.add(ctxt1, ctxt2, ctxt_sum);

    evaluator.multiply(ctxt1, ctxt2, ctxt_prod);
    evaluator.relinearize_inplace(ctxt_prod, relinKeys);
    evaluator.rescale_to_next_inplace(ctxt_prod);

    seal::Plaintext dec_sum, dec_prod;
    decryptor.decrypt(ctxt_sum, dec_sum);
    decryptor.decrypt(ctxt_prod, dec_prod);

    std::vector<double> res_sum, res_prod;
    encoder.decode(dec_sum, res_sum);
    encoder.decode(dec_prod, res_prod);

    std::cout << "Suma desencriptada: ";
    for (size_t i = 0; i < 2; ++i)
        std::cout << res_sum[i] << " ";
    std::cout << "\n";

    std::cout << "Producto desencriptado: ";
    for (size_t i = 0; i < 2; ++i)
        std::cout << res_prod[i] << " ";
    std::cout << "\n";

    return 0;
}
