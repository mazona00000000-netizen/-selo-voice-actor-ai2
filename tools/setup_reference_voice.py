"""إعداد تسجيل مرجعي لصوت الراوي داخل استوديو الراوي.

الاستخدام:
  python tools/setup_reference_voice.py "sample.wav" "النص المنطوق حرفيًا" --name "صوتي"

ضع التسجيل بصيغة WAV واضحة (5-15 ثانية) والنص المطابق له حرفيًا.
السكربت لا يرفع التسجيل إلى GitHub ولا يدرّب نموذجًا؛ يحفظه محليًا
ليستخدمه محرك Chatterbox كمرجع صوتي، أو VoiceTut مع النص المرجعي.
"""
from __future__ import annotations

import argparse
import re
import shutil
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REFERENCES = ROOT / "references"


def main() -> int:
    parser = argparse.ArgumentParser(description="إعداد عينة صوت مرجعية محلية")
    parser.add_argument("audio", help="ملف WAV")
    parser.add_argument("transcript", help="الكلمات المنطوقة في التسجيل حرفيًا")
    parser.add_argument("--name", default="SeloVoice", help="اسم الصوت")
    args = parser.parse_args()

    source = Path(args.audio).expanduser().resolve()
    transcript = args.transcript.strip()
    name = re.sub(r"[^\w-]+", "_", args.name, flags=re.UNICODE).strip("_")
    if not source.is_file():
        parser.error("ملف الصوت غير موجود.")
    if source.suffix.lower() != ".wav":
        parser.error("حوّل التسجيل إلى WAV أولًا (PCM، قناة واحدة أو قناتان).")
    if not transcript:
        parser.error("النص المطابق للتسجيل مطلوب.")
    try:
        with wave.open(str(source), "rb") as wav:
            duration = wav.getnframes() / float(wav.getframerate())
            channels = wav.getnchannels()
            rate = wav.getframerate()
    except wave.Error as exc:
        parser.error(f"ملف WAV غير صالح: {exc}")
    if not 3 <= duration <= 30:
        parser.error(f"مدة التسجيل {duration:.1f} ثانية؛ استخدم عينة من 5 إلى 15 ثانية (المسموح 3-30).")
    if not 16000 <= rate <= 48000:
        parser.error("معدل العينة يجب أن يكون بين 16 و48 kHz.")

    folder = REFERENCES / name
    folder.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, folder / "default.wav")
    (folder / "default.txt").write_text(transcript + "\n", encoding="utf-8")
    print(f"تم إعداد المرجع محليًا: {folder}")
    print(f"المدة: {duration:.1f}s | القنوات: {channels} | العينة: {rate} Hz")
    print("اختر الصوت 'SeloVoice' من جدول الأصوات بعد إعادة تشغيل التطبيق.")
    print("مهم: هذه عينة مرجعية للتوجيه الصوتي وليست تدريبًا أو استنساخًا مضمونًا للصوت.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
