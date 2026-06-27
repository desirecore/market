use aes_gcm::aead::{Aead, OsRng};
use aes_gcm::{AeadCore, Aes256Gcm, Key, KeyInit};
use anyhow::Result;

/// AES-GCM nonce size (96 bits).
const NONCE_SIZE: usize = 12;
/// AES-GCM authentication tag size (128 bits).
const TAG_SIZE: usize = 16;

/// Encrypt `plaintext` with AES-256-GCM. Returns `nonce || ciphertext`.
pub fn encrypt(key: &[u8; 32], plaintext: &[u8]) -> Result<Vec<u8>> {
    let cipher = Aes256Gcm::new(Key::<Aes256Gcm>::from_slice(key));
    let nonce = Aes256Gcm::generate_nonce(&mut OsRng);
    let ciphertext = cipher
        .encrypt(&nonce, plaintext)
        .map_err(|e| anyhow::anyhow!("数据加密失败：{e}"))?;

    let mut out = nonce.to_vec();
    out.extend(ciphertext);
    Ok(out)
}

/// Decrypt `data` (expected format: `nonce || ciphertext || tag`) with AES-256-GCM.
pub fn decrypt(key: &[u8; 32], data: &[u8]) -> Result<Vec<u8>> {
    if data.len() < NONCE_SIZE + TAG_SIZE {
        return Err(anyhow::anyhow!("数据解密失败（数据可能已损坏或被截断）",));
    }
    let (nonce_bytes, ciphertext) = data.split_at(NONCE_SIZE);
    let nonce = aes_gcm::Nonce::from_slice(nonce_bytes);
    let cipher = Aes256Gcm::new(Key::<Aes256Gcm>::from_slice(key));
    cipher
        .decrypt(nonce, ciphertext)
        .map_err(|e| anyhow::anyhow!("数据解密失败：{e}"))
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::crypto::keystore::generate_random_key;

    #[test]
    fn encrypt_decrypt_roundtrip() {
        let key = generate_random_key();
        let plaintext = b"hello, AES-256-GCM!";

        let encrypted = encrypt(&key, plaintext).unwrap();
        let decrypted = decrypt(&key, &encrypted).unwrap();

        assert_eq!(decrypted, plaintext);
    }

    #[test]
    fn encrypt_decrypt_empty_plaintext() {
        let key = generate_random_key();

        let encrypted = encrypt(&key, b"").unwrap();
        let decrypted = decrypt(&key, &encrypted).unwrap();

        assert_eq!(decrypted, b"");
    }

    #[test]
    fn encrypted_output_has_expected_length() {
        let key = generate_random_key();
        let plaintext = b"test data";

        let encrypted = encrypt(&key, plaintext).unwrap();
        // nonce (12) + plaintext (9) + tag (16) = 37
        assert_eq!(encrypted.len(), NONCE_SIZE + plaintext.len() + TAG_SIZE);
    }

    #[test]
    fn decrypt_with_wrong_key_fails() {
        let key1 = generate_random_key();
        let key2 = generate_random_key();

        let encrypted = encrypt(&key1, b"secret").unwrap();
        assert!(decrypt(&key2, &encrypted).is_err());
    }

    #[test]
    fn decrypt_too_short_data_fails() {
        let key = generate_random_key();

        // Less than NONCE_SIZE + TAG_SIZE = 28
        assert!(decrypt(&key, &[0u8; 27]).is_err());
        assert!(decrypt(&key, &[]).is_err());
        assert!(decrypt(&key, &[0u8; 11]).is_err());
    }

    #[test]
    fn decrypt_corrupted_data_fails() {
        let key = generate_random_key();
        let encrypted = encrypt(&key, b"important data").unwrap();

        // Flip a byte in the ciphertext portion
        let mut corrupted = encrypted.clone();
        let last = corrupted.len() - 1;
        corrupted[last] ^= 0xFF;

        assert!(decrypt(&key, &corrupted).is_err());
    }

    #[test]
    fn each_encryption_produces_different_output() {
        let key = generate_random_key();
        let plaintext = b"same plaintext";

        let a = encrypt(&key, plaintext).unwrap();
        let b = encrypt(&key, plaintext).unwrap();

        // Different nonces → different ciphertext
        assert_ne!(a, b);
        // But both decrypt to the same plaintext
        assert_eq!(decrypt(&key, &a).unwrap(), plaintext);
        assert_eq!(decrypt(&key, &b).unwrap(), plaintext);
    }
}
