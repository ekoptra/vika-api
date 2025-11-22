"""
Seeder untuk membuat dummy data analytics
Menggunakan Faker library untuk generate data realistis
"""
import random
import json
from datetime import datetime, timedelta, timezone
from faker import Faker
import hashlib
import uuid
from sqlalchemy.orm import Session
from database.base import SessionLocal
from database.models.user import User
from database.models.session import Session as SessionModel
from database.models.session_conversation import SessionConversation, ConversationRole
from argon2 import PasswordHasher

# Initialize Faker and Password Hasher
fake = Faker(['id_ID'])  # Indonesian locale
ph = PasswordHasher()

# List screen yang tersedia
SCREENS = [
    {"keywords": ["info", "umum"], "deep_link": "bpjskes://info_program_jkn", "screen_id": "info_program_jkn", "description": "Menu ini berisi rangkuman menyeluruh mengenai Program Jaminan Kesehatan Nasional (JKN)", "screen_name": "Info Program JKN"},
    {"keywords": ["telehealth", "konsultasi", "dokter", "online", "kesehatan"], "deep_link": "bpjskes://telehealth", "screen_id": "telehealth", "description": "Telehealth memberikan akses konsultasi kesehatan jarak jauh dengan tenaga medis", "screen_name": "Telehealth"},
    {"keywords": ["riwayat", "pelayanan", "faskes", "kunjungan", "medis"], "deep_link": "bpjskes://info_riwayat_pelayanan", "screen_id": "info_riwayat_pelayanan", "description": "Menu ini menyajikan daftar lengkap pelayanan kesehatan yang pernah diterima peserta", "screen_name": "Info Riwayat Pelayanan"},
    {"keywords": ["sehat", "bugar", "gaya", "hidup", "edukasi"], "deep_link": "bpjskes://bugar", "screen_id": "bugar", "description": "Menu Bugar menyediakan konten edukatif mengenai gaya hidup sehat", "screen_name": "Bugar"},
    {"keywords": ["rehap", "cicilan", "tunggakan", "iuran", "pembayaran"], "deep_link": "bpjskes://new_rehap", "screen_id": "new_rehap", "description": "Fitur ini memungkinkan peserta mensimulasikan dan mengatur pembayaran tunggakan iuran", "screen_name": "Cicilan REHAP"},
    {"keywords": ["penambahan", "peserta", "keluarga", "pendaftaran", "data"], "deep_link": "bpjskes://penambahan_peserta", "screen_id": "penambahan_peserta", "description": "Menu ini digunakan untuk menambahkan anggota keluarga ke dalam kepesertaan JKN", "screen_name": "Penambahan Peserta"},
    {"keywords": ["peserta", "informasi", "kepesertaan", "data", "profil"], "deep_link": "bpjskes://info_peserta", "screen_id": "info_peserta", "description": "Menu ini memuat informasi lengkap mengenai status kepesertaan", "screen_name": "Info Peserta"},
    {"keywords": ["sos", "darurat", "bantuan", "gawat", "kontak"], "deep_link": "bpjskes://sos", "screen_id": "sos", "description": "Menu SOS menyediakan akses cepat menuju informasi dan panduan tindakan awal ketika menghadapi kondisi darurat", "screen_name": "SOS"},
    {"keywords": ["faskes", "lokasi", "peta", "pelayanan", "kesehatan"], "deep_link": "bpjskes://info_lokasi_faskes", "screen_id": "info_lokasi_faskes", "description": "Fitur ini menampilkan daftar lengkap fasilitas kesehatan yang bekerja sama dengan BPJS", "screen_name": "Info Lokasi Faskes"},
    {"keywords": ["perubahan", "data", "peserta", "update", "profil"], "deep_link": "bpjskes://perubahan_data_peserta", "screen_id": "perubahan_data_peserta", "description": "Menu ini digunakan untuk memperbarui informasi kepesertaan", "screen_name": "Perubahan Data Peserta"},
    {"keywords": ["pengaduan", "keluhan", "layanan", "jkn", "aduan"], "deep_link": "bpjskes://pengaduan_layanan_jkn", "screen_id": "pengaduan_layanan_jkn", "description": "Fitur ini memberikan sarana bagi peserta untuk menyampaikan keluhan", "screen_name": "Pengaduan Layanan JKN"},
    {"keywords": ["skrining", "kesehatan", "risiko", "mandiri", "medis"], "deep_link": "bpjskes://skrining_riwayat_kesehatan", "screen_id": "skrining_riwayat_kesehatan", "description": "Menu ini memungkinkan peserta melakukan skrining mandiri", "screen_name": "Skrining Riwayat Kesehatan"},
    {"keywords": ["antrean", "pendaftaran", "online", "pelayanan", "faskes"], "deep_link": "bpjskes://pendaftaran_pelayanan", "screen_id": "pendaftaran_pelayanan", "description": "Fitur antrean online memungkinkan peserta mendaftar layanan", "screen_name": "Pendaftaran Pelayanan"},
    {"keywords": ["tempat", "tidur", "tersedia", "rujukan", "inap"], "deep_link": "bpjskes://info_ketersediaan_tempat_tidur", "screen_id": "info_ketersediaan_tempat_tidur", "description": "Fitur ini menampilkan informasi terbaru mengenai jumlah tempat tidur kosong", "screen_name": "Info Ketersediaan Tempat Tidur"},
    {"keywords": ["operasi", "jadwal", "tindakan", "medis", "rujukan"], "deep_link": "bpjskes://info_jadwal_tindakan_operasi", "screen_id": "info_jadwal_tindakan_operasi", "description": "Menu ini memberikan informasi jadwal tindakan operasi", "screen_name": "Info Jadwal Tindakan Operasi"},
    {"keywords": ["iuran", "pembayaran", "tarif", "kepesertaan", "biaya"], "deep_link": "bpjskes://info_iuran", "screen_id": "info_iuran", "description": "Fitur ini menyediakan rangkuman lengkap mengenai besaran iuran", "screen_name": "Info Iuran"},
    {"keywords": ["auto", "debit", "pembayaran", "iuran", "otomatis"], "deep_link": "bpjskes://pendaftaran_auto_debit", "screen_id": "pendaftaran_auto_debit", "description": "Menu ini memudahkan peserta mengaktifkan fitur auto debit", "screen_name": "Pendaftaran Auto Debit"},
    {"keywords": ["riwayat", "pembayaran", "iuran", "transaksi", "catatan"], "deep_link": "bpjskes://info_riwayat_pembayaran", "screen_id": "info_riwayat_pembayaran", "description": "Menu ini menampilkan catatan seluruh pembayaran iuran", "screen_name": "Info Riwayat Pembayaran"},
    {"keywords": ["virtual", "account", "pembayaran", "iuran", "va"], "deep_link": "bpjskes://info_virtual_account", "screen_id": "info_virtual_account", "description": "Fitur ini menyediakan informasi nomor virtual account peserta", "screen_name": "Info Virtual Account"},
    {"keywords": ["obat", "pengingat", "kesehatan", "dosis", "konsumsi"], "deep_link": "bpjskes://minum_obat", "screen_id": "minum_obat", "description": "Menu Minum Obat membantu peserta mengatur jadwal konsumsi obat", "screen_name": "Minum Obat"},
    {"keywords": ["penyakit", "tren", "daerah", "statistik", "kesehatan"], "deep_link": "bpjskes://tren_penyakit_daerah", "screen_id": "tren_penyakit_daerah", "description": "Fitur ini menyajikan data statistik mengenai tren penyakit", "screen_name": "Tren Penyakit Daerah"},
    {"keywords": ["antrean", "online", "faskes", "pelayanan", "jadwal"], "deep_link": "bpjskes://antrean_online", "screen_id": "antrean_online", "description": "Menu ini menyediakan fitur antrean digital", "screen_name": "Antrean Online"}
]


def generate_api_key():
    """Generate random API key"""
    return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()


def generate_user_questions():
    """Generate realistic user questions in Indonesian"""
    questions = [
        "Bagaimana cara cek iuran BPJS saya?",
        "Tolong buka info riwayat pelayanan",
        "Saya mau lihat jadwal tindakan operasi",
        "Dimana lokasi faskes terdekat?",
        "Bagaimana cara daftar antrean online?",
        "Mau cek virtual account untuk pembayaran",
        "Tampilkan info ketersediaan tempat tidur",
        "Bagaimana cara konsultasi dengan dokter online?",
        "Mau lihat riwayat pembayaran iuran saya",
        "Tolong buka halaman info peserta",
        "Saya butuh info tentang program JKN",
        "Bagaimana cara mengubah data peserta?",
        "Mau tambah anggota keluarga ke BPJS",
        "Tolong buka menu bugar",
        "Saya mau cicilan iuran REHAP",
        "Bagaimana cara lapor keluhan pelayanan?",
        "Mau cek tren penyakit di daerah saya",
        "Tolong aktifkan auto debit pembayaran",
        "Saya perlu skrining kesehatan",
        "Mau setting pengingat minum obat",
    ]
    return random.choice(questions)


def generate_ai_responses(screen=None):
    """Generate AI response with or without navigation"""
    responses_with_nav = [
        "Baik, saya arahkan Anda ke halaman {}.",
        "Tentu, berikut saya buka halaman {}.",
        "Silakan, saya tampilkan halaman {} untuk Anda.",
        "Oke, membuka halaman {} sekarang.",
    ]

    responses_without_nav = [
        "Saya dapat membantu Anda dengan itu. Apakah Anda ingin saya arahkan ke halaman terkait?",
        "Untuk informasi lebih detail, saya bisa membukakan halaman yang sesuai. Apakah Anda mau?",
        "Baik, saya mengerti pertanyaan Anda. Apakah ada yang bisa saya bantu lagi?",
        "Terima kasih atas pertanyaannya. Saya siap membantu Anda.",
    ]

    if screen:
        screen_name = screen["screen_name"]
        return random.choice(responses_with_nav).format(screen_name)
    else:
        return random.choice(responses_without_nav)


def create_seed_data(db: Session):
    """Create seed data for analytics testing"""

    print("🌱 Starting seed process...")

    # 1. Create user
    print("\n📝 Creating user...")
    user_email = "demo@gmail.com"

    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_email).first()
    if existing_user:
        print(f"⚠️  User {user_email} already exists. Deleting old user and creating new one...")
        db.delete(existing_user)
        db.commit()

    user = User(
        nama="Demo Analytics User",
        email=user_email,
        password=ph.hash("password123"),  # Use Argon2 hash
        api_key=generate_api_key()
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"✅ User created: {user.email}")
    print(f"🔑 API Key: {user.api_key}")

    # 2. Create sessions (spread over 30 days)
    print("\n📅 Creating sessions...")
    sessions = []
    num_sessions = 15  # 15 sessions over 30 days

    for i in range(num_sessions):
        # Random date in the last 30 days
        days_ago = random.randint(0, 29)
        session_date = datetime.now(timezone.utc) - timedelta(days=days_ago)

        session = SessionModel(
            user_id=user.id,
            screen_list=SCREENS,
            expired_at=session_date + timedelta(hours=24),
            created_at=session_date
        )
        db.add(session)
        sessions.append(session)

    db.commit()
    print(f"✅ Created {len(sessions)} sessions")

    # 3. Create conversations with screen navigation
    print("\n💬 Creating conversations...")
    total_conversations = 0
    total_navigations = 0

    # Weight for popular screens (some screens are accessed more frequently)
    popular_screen_indices = [0, 2, 6, 8, 12, 15, 17]  # Popular screens

    for session in sessions:
        # Each session has 3-8 conversation pairs
        num_pairs = random.randint(3, 8)

        for pair_idx in range(num_pairs):
            # User message
            user_conv = SessionConversation(
                session_id=session.id,
                role=ConversationRole.user,
                text_transcript=generate_user_questions(),
                audio_path=f"/uploads/audio_{uuid.uuid4()}.mp3",
                audio_size=random.randint(10000, 50000),
                created_at=session.created_at + timedelta(minutes=pair_idx * 5)
            )
            db.add(user_conv)
            total_conversations += 1

            # AI response - 70% chance of navigation
            has_navigation = random.random() < 0.7
            selected_screen = None
            navigation_obj = None

            if has_navigation:
                # Choose screen (weighted towards popular screens)
                if random.random() < 0.6:
                    # Popular screen
                    screen_idx = random.choice(popular_screen_indices)
                else:
                    # Any screen
                    screen_idx = random.randint(0, len(SCREENS) - 1)

                selected_screen = SCREENS[screen_idx]
                navigation_obj = {
                    "screen_id": selected_screen["screen_id"],
                    "screen_name": selected_screen["screen_name"],
                    "deep_link": selected_screen["deep_link"]
                }
                total_navigations += 1

            user_question = user_conv.text_transcript
            reply_text = generate_ai_responses(selected_screen)
            reply_audio_url = f"/audio/reply_{uuid.uuid4()}.mp3"

            ai_conv = SessionConversation(
                session_id=session.id,
                role=ConversationRole.ai,
                text_transcript=reply_text,
                response_json={
                    "navigation": navigation_obj,
                    "reply_text": reply_text,
                    "transcription": user_question,
                    "reply_audio_url": reply_audio_url
                },
                audio_path=reply_audio_url,
                audio_size=random.randint(15000, 60000),
                created_at=session.created_at + timedelta(minutes=pair_idx * 5, seconds=30)
            )
            db.add(ai_conv)
            total_conversations += 1

    db.commit()
    print(f"✅ Created {total_conversations} conversations")
    print(f"🎯 With {total_navigations} screen navigations")

    # 4. Summary
    print("\n" + "="*60)
    print("🎉 SEED COMPLETED!")
    print("="*60)
    print(f"\n👤 User Account:")
    print(f"   Email: {user.email}")
    print(f"   Password: password123")
    print(f"   API Key: {user.api_key}")
    print(f"\n📊 Statistics:")
    print(f"   Sessions: {len(sessions)}")
    print(f"   Conversations: {total_conversations}")
    print(f"   Navigations: {total_navigations}")
    print(f"   Navigation Rate: {total_navigations / (total_conversations / 2) * 100:.1f}%")
    print(f"\n🌐 Login URL: http://localhost:8000/login")
    print(f"📊 Dashboard URL: http://localhost:8000/dashboard")
    print("\n" + "="*60)


if __name__ == "__main__":
    db = SessionLocal()
    try:
        create_seed_data(db)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()
