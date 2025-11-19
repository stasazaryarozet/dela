#!/usr/bin/env python3
"""
AUDIO PREPROCESSOR MODULE
Профессиональная предобработка аудио для улучшения качества распознавания речи

Архитектура:
- Модульный дизайн (каждый фильтр — отдельная функция)
- Pipeline pattern для композиции фильтров
- Изолированность (легко подключить/отключить)
- Метрики качества (до/после)
- Логирование операций

Best Practices:
- Type hints для всех функций
- Docstrings в Google Style
- Defensive programming (валидация входных данных)
- Resource management (context managers)
- Error handling с информативными сообщениями
"""

from pathlib import Path
from typing import Optional, List, Callable, Dict, Any
from dataclasses import dataclass
import json
import time
import logging

# Опциональный импорт ffmpeg-python
try:
    import ffmpeg
    FFMPEG_AVAILABLE = True
except ImportError:
    FFMPEG_AVAILABLE = False
    logging.warning(
        "ffmpeg-python not installed. Audio preprocessing disabled. "
        "Install with: pip install ffmpeg-python"
    )


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class AudioMetrics:
    """Метрики качества аудио"""
    duration_sec: float
    sample_rate: int
    channels: int
    bitrate: Optional[int] = None
    codec: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'duration_sec': self.duration_sec,
            'sample_rate': self.sample_rate,
            'channels': self.channels,
            'bitrate': self.bitrate,
            'codec': self.codec
        }


@dataclass
class PreprocessingResult:
    """Результат предобработки"""
    output_file: Path
    original_metrics: AudioMetrics
    processed_metrics: AudioMetrics
    filters_applied: List[str]
    processing_time_sec: float
    success: bool
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'output_file': str(self.output_file),
            'original_metrics': self.original_metrics.to_dict(),
            'processed_metrics': self.processed_metrics.to_dict(),
            'filters_applied': self.filters_applied,
            'processing_time_sec': round(self.processing_time_sec, 3),
            'success': self.success,
            'error_message': self.error_message
        }


# ============================================================================
# AUDIO FILTERS (Modular Design)
# ============================================================================

class AudioFilter:
    """Базовый класс для аудио-фильтров"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    def apply(self, stream) -> Any:
        """
        Применяет фильтр к ffmpeg stream
        
        Args:
            stream: ffmpeg stream object
            
        Returns:
            Модифицированный stream
        """
        raise NotImplementedError
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"


class NoiseReductionFilter(AudioFilter):
    """Фильтр шумоподавления (Adaptive FFT Denoiser)"""
    
    def __init__(self, noise_reduction: int = 10, noise_floor: int = -25):
        """
        Args:
            noise_reduction: Уровень шумоподавления (0-97, default: 10)
            noise_floor: Порог шума в dB (-80 to 20, default: -25)
        """
        super().__init__("noise_reduction")
        self.noise_reduction = max(0, min(97, noise_reduction))
        self.noise_floor = max(-80, min(20, noise_floor))
    
    def apply(self, stream) -> Any:
        self.logger.info(f"Applying noise reduction: nr={self.noise_reduction}, nf={self.noise_floor}dB")
        return stream.filter('afftdn', nr=self.noise_reduction, nf=self.noise_floor)


class LoudnessNormalizationFilter(AudioFilter):
    """Фильтр нормализации громкости (EBU R128 standard)"""
    
    def __init__(self, integrated: int = -16, true_peak: float = -1.5, lra: int = 11):
        """
        Args:
            integrated: Integrated loudness target (LUFS, default: -16)
            true_peak: True peak target (dBTP, default: -1.5)
            lra: Loudness range target (LU, default: 11)
        """
        super().__init__("loudness_normalization")
        self.integrated = integrated
        self.true_peak = true_peak
        self.lra = lra
    
    def apply(self, stream) -> Any:
        self.logger.info(f"Applying loudness normalization: I={self.integrated} LUFS, TP={self.true_peak} dBTP")
        return stream.filter('loudnorm', I=self.integrated, TP=self.true_peak, LRA=self.lra)


class MonoConversionFilter(AudioFilter):
    """Фильтр конвертации в моно"""
    
    def __init__(self):
        super().__init__("mono_conversion")
    
    def apply(self, stream) -> Any:
        self.logger.info("Converting to mono (1 channel)")
        # Смешиваем каналы с равными весами
        return stream.filter('pan', 'mono|c0=0.5*c0+0.5*c1')


class SilenceRemovalFilter(AudioFilter):
    """Фильтр удаления тишины"""
    
    def __init__(self, threshold: str = '-50dB', duration: float = 0.5):
        """
        Args:
            threshold: Порог тишины (default: -50dB)
            duration: Минимальная длительность тишины для удаления (сек, default: 0.5)
        """
        super().__init__("silence_removal")
        self.threshold = threshold
        self.duration = duration
    
    def apply(self, stream) -> Any:
        self.logger.info(f"Removing silence: threshold={self.threshold}, duration={self.duration}s")
        return stream.filter(
            'silenceremove',
            start_periods=1,
            start_threshold=self.threshold,
            start_duration=self.duration,
            stop_periods=1,
            stop_threshold=self.threshold,
            stop_duration=self.duration
        )


class HighPassFilter(AudioFilter):
    """Высокочастотный фильтр (удаляет низкие частоты)"""
    
    def __init__(self, frequency: int = 200):
        """
        Args:
            frequency: Частота среза в Hz (default: 200, убирает низкочастотный шум)
        """
        super().__init__("highpass")
        self.frequency = frequency
    
    def apply(self, stream) -> Any:
        self.logger.info(f"Applying highpass filter: f={self.frequency} Hz")
        return stream.filter('highpass', f=self.frequency, poles=2)


class LowPassFilter(AudioFilter):
    """Низкочастотный фильтр (удаляет высокие частоты)"""
    
    def __init__(self, frequency: int = 3400):
        """
        Args:
            frequency: Частота среза в Hz (default: 3400, для речи достаточно)
        """
        super().__init__("lowpass")
        self.frequency = frequency
    
    def apply(self, stream) -> Any:
        self.logger.info(f"Applying lowpass filter: f={self.frequency} Hz")
        return stream.filter('lowpass', f=self.frequency, poles=2)


# ============================================================================
# PREPROCESSOR (Main Class)
# ============================================================================

class AudioPreprocessor:
    """
    Профессиональный препроцессор аудио для распознавания речи
    
    Архитектурные принципы:
    - Pipeline Pattern: композиция фильтров
    - Single Responsibility: каждый фильтр — одна задача
    - Open/Closed: легко добавлять новые фильтры
    - Dependency Injection: фильтры передаются извне
    """
    
    # Предустановленные профили
    PROFILES = {
        'clean': {
            'description': 'Минимальная обработка для чистых записей',
            'filters': ['mono_conversion', 'silence_removal']
        },
        'standard': {
            'description': 'Стандартная обработка для большинства записей',
            'filters': ['noise_reduction', 'loudness_normalization', 'mono_conversion', 'silence_removal']
        },
        'aggressive': {
            'description': 'Агрессивная обработка для проблемных записей',
            'filters': ['highpass', 'noise_reduction', 'lowpass', 'loudness_normalization', 'mono_conversion', 'silence_removal']
        },
        'speech_optimized': {
            'description': 'Оптимизация для распознавания речи',
            'filters': ['highpass', 'noise_reduction', 'loudness_normalization', 'mono_conversion']
        }
    }
    
    def __init__(
        self,
        target_sample_rate: int = 16000,
        target_codec: str = 'libmp3lame',
        target_bitrate: str = '128k',
        logger: Optional[logging.Logger] = None
    ):
        """
        Args:
            target_sample_rate: Целевая частота дискретизации (Hz, default: 16000)
            target_codec: Целевой кодек (default: libmp3lame для MP3)
            target_bitrate: Целевой битрейт (default: 128k)
            logger: Опциональный logger
        """
        if not FFMPEG_AVAILABLE:
            raise RuntimeError(
                "ffmpeg-python is required for audio preprocessing. "
                "Install with: pip install ffmpeg-python"
            )
        
        self.target_sample_rate = target_sample_rate
        self.target_codec = target_codec
        self.target_bitrate = target_bitrate
        self.logger = logger or logging.getLogger(__name__)
        
        # Регистр доступных фильтров
        self._filter_registry = {
            'noise_reduction': NoiseReductionFilter(),
            'loudness_normalization': LoudnessNormalizationFilter(),
            'mono_conversion': MonoConversionFilter(),
            'silence_removal': SilenceRemovalFilter(),
            'highpass': HighPassFilter(),
            'lowpass': LowPassFilter()
        }
    
    def register_filter(self, name: str, filter_instance: AudioFilter) -> None:
        """
        Регистрирует пользовательский фильтр
        
        Args:
            name: Уникальное имя фильтра
            filter_instance: Экземпляр AudioFilter
        """
        self._filter_registry[name] = filter_instance
        self.logger.info(f"Registered custom filter: {name}")
    
    def get_audio_metrics(self, file_path: Path) -> AudioMetrics:
        """
        Извлекает метрики аудио файла
        
        Args:
            file_path: Путь к аудио файлу
            
        Returns:
            AudioMetrics с характеристиками файла
        """
        try:
            probe = ffmpeg.probe(str(file_path))
            audio_stream = next(
                (s for s in probe['streams'] if s['codec_type'] == 'audio'),
                None
            )
            
            if not audio_stream:
                raise ValueError(f"No audio stream found in {file_path}")
            
            return AudioMetrics(
                duration_sec=float(probe['format'].get('duration', 0)),
                sample_rate=int(audio_stream.get('sample_rate', 0)),
                channels=int(audio_stream.get('channels', 0)),
                bitrate=int(probe['format'].get('bit_rate', 0)) if 'bit_rate' in probe['format'] else None,
                codec=audio_stream.get('codec_name')
            )
        
        except Exception as e:
            self.logger.error(f"Failed to extract audio metrics: {e}")
            raise
    
    def process(
        self,
        input_file: Path,
        output_file: Optional[Path] = None,
        profile: str = 'standard',
        custom_filters: Optional[List[str]] = None,
        save_metrics: bool = True
    ) -> PreprocessingResult:
        """
        Обрабатывает аудио файл
        
        Args:
            input_file: Путь к входному файлу
            output_file: Путь к выходному файлу (опционально)
            profile: Предустановленный профиль ('clean', 'standard', 'aggressive', 'speech_optimized')
            custom_filters: Список пользовательских фильтров (перекрывает profile)
            save_metrics: Сохранить метрики в .json файл
            
        Returns:
            PreprocessingResult с результатами обработки
            
        Raises:
            FileNotFoundError: Если входной файл не найден
            ValueError: Если профиль неизвестен
            RuntimeError: Если обработка не удалась
        """
        start_time = time.time()
        
        # Валидация входных данных
        input_file = Path(input_file)
        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        # Определяем выходной файл
        if output_file is None:
            output_file = input_file.parent / f"{input_file.stem}_preprocessed{input_file.suffix}"
        else:
            output_file = Path(output_file)
        
        # Создаем директорию если нужно
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Определяем фильтры
        if custom_filters:
            filters_to_apply = custom_filters
        elif profile in self.PROFILES:
            filters_to_apply = self.PROFILES[profile]['filters']
        else:
            raise ValueError(
                f"Unknown profile: {profile}. "
                f"Available profiles: {', '.join(self.PROFILES.keys())}"
            )
        
        self.logger.info(f"Processing: {input_file.name}")
        self.logger.info(f"Profile: {profile}")
        self.logger.info(f"Filters: {', '.join(filters_to_apply)}")
        
        try:
            # Извлекаем метрики оригинала
            original_metrics = self.get_audio_metrics(input_file)
            self.logger.info(
                f"Original: {original_metrics.sample_rate} Hz, "
                f"{original_metrics.channels} ch, "
                f"{original_metrics.duration_sec:.1f}s"
            )
            
            # Создаем ffmpeg stream
            stream = ffmpeg.input(str(input_file))
            
            # Применяем фильтры последовательно
            for filter_name in filters_to_apply:
                if filter_name not in self._filter_registry:
                    self.logger.warning(f"Unknown filter: {filter_name}, skipping")
                    continue
                
                filter_instance = self._filter_registry[filter_name]
                stream = filter_instance.apply(stream)
            
            # Применяем выходные параметры
            stream = stream.output(
                str(output_file),
                acodec=self.target_codec,
                audio_bitrate=self.target_bitrate,
                ar=self.target_sample_rate,
                format='mp3' if self.target_codec == 'libmp3lame' else None
            )
            
            # Выполняем обработку
            stream.run(overwrite_output=True, quiet=True, capture_stderr=True)
            
            # Извлекаем метрики результата
            processed_metrics = self.get_audio_metrics(output_file)
            processing_time = time.time() - start_time
            
            self.logger.info(
                f"Processed: {processed_metrics.sample_rate} Hz, "
                f"{processed_metrics.channels} ch, "
                f"{processed_metrics.duration_sec:.1f}s, "
                f"time: {processing_time:.2f}s"
            )
            
            result = PreprocessingResult(
                output_file=output_file,
                original_metrics=original_metrics,
                processed_metrics=processed_metrics,
                filters_applied=filters_to_apply,
                processing_time_sec=processing_time,
                success=True
            )
            
            # Сохраняем метрики
            if save_metrics:
                metrics_file = output_file.with_suffix('.preprocessing.json')
                with open(metrics_file, 'w', encoding='utf-8') as f:
                    json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
                self.logger.info(f"Metrics saved: {metrics_file.name}")
            
            return result
        
        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = f"Preprocessing failed: {str(e)}"
            self.logger.error(error_msg)
            
            return PreprocessingResult(
                output_file=output_file,
                original_metrics=original_metrics if 'original_metrics' in locals() else None,
                processed_metrics=None,
                filters_applied=filters_to_apply,
                processing_time_sec=processing_time,
                success=False,
                error_message=error_msg
            )


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def preprocess_audio(
    input_file: Path | str,
    output_file: Optional[Path | str] = None,
    profile: str = 'standard',
    enabled: bool = True
) -> Optional[Path]:
    """
    Удобная функция для предобработки аудио
    
    Args:
        input_file: Путь к входному файлу
        output_file: Путь к выходному файлу (опционально)
        profile: Профиль обработки ('clean', 'standard', 'aggressive', 'speech_optimized')
        enabled: Включить/выключить предобработку
        
    Returns:
        Path к обработанному файлу или None если disabled/failed
    """
    if not enabled:
        return None
    
    if not FFMPEG_AVAILABLE:
        logging.warning("Audio preprocessing disabled: ffmpeg-python not installed")
        return None
    
    try:
        preprocessor = AudioPreprocessor()
        result = preprocessor.process(
            input_file=Path(input_file),
            output_file=Path(output_file) if output_file else None,
            profile=profile
        )
        
        return result.output_file if result.success else None
    
    except Exception as e:
        logging.error(f"Preprocessing failed: {e}")
        return None


# ============================================================================
# CLI INTERFACE
# ============================================================================

if __name__ == '__main__':
    import argparse
    
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    parser = argparse.ArgumentParser(
        description='Professional audio preprocessor for speech recognition',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Available profiles:
{chr(10).join(f"  {name}: {info['description']}" for name, info in AudioPreprocessor.PROFILES.items())}

Examples:
  # Standard processing
  python audio_preprocessor.py input.mp4 -o output.mp3
  
  # Aggressive processing for noisy audio
  python audio_preprocessor.py input.mp4 -p aggressive
  
  # Custom filters
  python audio_preprocessor.py input.mp4 -f noise_reduction loudness_normalization
"""
    )
    
    parser.add_argument('input', type=str, help='Input audio/video file')
    parser.add_argument('-o', '--output', type=str, help='Output file (optional)')
    parser.add_argument(
        '-p', '--profile',
        type=str,
        default='standard',
        choices=list(AudioPreprocessor.PROFILES.keys()),
        help='Processing profile (default: standard)'
    )
    parser.add_argument(
        '-f', '--filters',
        nargs='+',
        help='Custom filter list (overrides profile)'
    )
    parser.add_argument(
        '--sample-rate',
        type=int,
        default=16000,
        help='Target sample rate in Hz (default: 16000)'
    )
    parser.add_argument(
        '--no-metrics',
        action='store_true',
        help='Do not save metrics to JSON'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if not FFMPEG_AVAILABLE:
        print("ERROR: ffmpeg-python is not installed.")
        print("Install with: pip install ffmpeg-python")
        exit(1)
    
    try:
        preprocessor = AudioPreprocessor(target_sample_rate=args.sample_rate)
        
        result = preprocessor.process(
            input_file=Path(args.input),
            output_file=Path(args.output) if args.output else None,
            profile=args.profile,
            custom_filters=args.filters,
            save_metrics=not args.no_metrics
        )
        
        if result.success:
            print(f"\n✅ Success!")
            print(f"   Output: {result.output_file}")
            print(f"   Filters: {', '.join(result.filters_applied)}")
            print(f"   Time: {result.processing_time_sec:.2f}s")
            exit(0)
        else:
            print(f"\n❌ Failed: {result.error_message}")
            exit(1)
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        exit(1)
