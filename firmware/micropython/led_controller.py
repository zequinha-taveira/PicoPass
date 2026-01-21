# firmware/micropython/led_controller.py

from machine import Pin, PWM
import time

class LEDController:
    """Controlador de LEDs com PWM"""
    
    def __init__(self):
        # LEDs em modo PWM para fade/blink suave
        # Using GPIOs from specification (16, 17, 18)
        # Note: RP2040 uses slices.
        self.led_status = PWM(Pin(16))    # Verde
        self.led_error = PWM(Pin(17))     # Vermelho
        self.led_activity = PWM(Pin(18))  # Azul
        
        # Frequência PWM
        self.led_status.freq(1000)
        self.led_error.freq(1000)
        self.led_activity.freq(1000)
        
        # Estado inicial
        self.all_off()
    
    def set_brightness(self, led, brightness):
        """Define brilho do LED (0-100)"""
        duty = int((brightness / 100) * 65535)
        led.duty_u16(duty)
    
    def set_status(self, on, brightness=100):
        """LED de status (verde)"""
        self.set_brightness(self.led_status, brightness if on else 0)
    
    def set_error(self, on, brightness=100):
        """LED de erro (vermelho)"""
        self.set_brightness(self.led_error, brightness if on else 0)
    
    def set_activity(self, on, brightness=100):
        """LED de atividade (azul)"""
        self.set_brightness(self.led_activity, brightness if on else 0)
    
    def all_off(self):
        """Desliga todos LEDs"""
        self.set_status(False)
        self.set_error(False)
        self.set_activity(False)
    
    def blink_status(self, times, delay=0.1):
        """Pisca LED de status"""
        original = self.led_status.duty_u16() > 0
        for _ in range(times):
            self.set_status(False)
            time.sleep(delay)
            self.set_status(True)
            time.sleep(delay)
        self.set_status(original)
    
    def blink_error(self, times, delay=0.1):
        """Pisca LED de erro"""
        original = self.led_error.duty_u16() > 0
        for _ in range(times):
            self.set_error(False)
            time.sleep(delay)
            self.set_error(True, 100)
            time.sleep(delay)
        self.set_error(original)
    
    def boot_animation(self):
        """Animação de boot"""
        # Fade in/out sequencial
        for led in [self.led_status, self.led_activity, self.led_error]:
            for brightness in range(0, 101, 10):
                self.set_brightness(led, brightness)
                time.sleep(0.02)
            for brightness in range(100, -1, -10):
                self.set_brightness(led, brightness)
                time.sleep(0.02)
        
        self.all_off()
    
    def waiting_pattern(self):
        """Padrão de espera (breathing)"""
        for _ in range(3):
            for brightness in range(0, 101, 5):
                self.set_status(True, brightness)
                time.sleep(0.01)
            for brightness in range(100, -1, -5):
                self.set_status(True, brightness)
                time.sleep(0.01)
    
    def pulse(self, led, duration=1.0):
        """Pulso suave em um LED"""
        steps = 50
        delay = duration / (steps * 2)
        
        for brightness in range(0, 101, int(100/steps)):
            self.set_brightness(led, brightness)
            time.sleep(delay)
        
        for brightness in range(100, -1, -int(100/steps)):
            self.set_brightness(led, brightness)
            time.sleep(delay)
