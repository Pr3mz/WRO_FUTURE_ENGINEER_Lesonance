#include "Wire.h"
#include "Arduino.h"
#include "Adafruit_GFX.h"
#include "OLED_I2C_SSD1309.h"
#include "Adafruit_NeoPixel.h"
#define OLED_RESET -1
#define ALL 12
#define ON   1
#define OFF  0

#define BUZZER_PIN          25
#define SOUND_PWM_CHANNEL   0
#define SOUND_RESOLUTION    8
#define SOUND_ON            (1<<(SOUND_RESOLUTION-1))
#define SOUND_OFF           0

#define i0  10
#define i1  11
#define i2  12
#define i3  13
#define i4  14
#define i5  15
#define i6  16
#define i7  17
#define LED  18

OLED_I2C_SSD1309 oled(OLED_RESET);

 
#define _NUMSLEDs  3
#define _PINSLEDs  12
Adafruit_NeoPixel sleds = Adafruit_NeoPixel(_NUMSLEDs,_PINSLEDs, NEO_GRB + NEO_KHZ800);

int iKBAddr = 0x48;
// init libraries ipst-wifi
void init(void){
	iKBAddr = 0x48;
	Wire.begin();
    Wire.beginTransmission(iKBAddr);
    Wire.write(0);
    Wire.endTransmission();
	
	oled.begin(SSD1309_SWITCHCAPVCC, 0x3C);  // initialize with the I2C addr 0x3D (for the 128x64)
    oled.show();
	sleds.begin(); 
	sleds.setBrightness(10);
	sleds.setPixelColor(0,0,0,0);
	sleds.setPixelColor(1,0,0,0);
	sleds.setPixelColor(2,0,0,0);
    sleds.show();

}
// Set Address iKBz
void init(int _addre){
   bool Check=true;
	oled.begin(SSD1309_SWITCHCAPVCC, 0x3C);  // initialize with the I2C addr 0x3D (for the 128x64)
    oled.show();
	sleds.begin(); 
	sleds.setBrightness(10);
	sleds.setPixelColor(0,0,0,0);
	sleds.setPixelColor(1,0,0,0);
	sleds.setPixelColor(2,0,0,0);
    sleds.show();
	
	iKBAddr = _addre;
	Wire.begin();
	if(Check==true){
		while(1){
		Wire.beginTransmission(iKBAddr);
		 uint8_t ec = Wire.endTransmission(true);
		 if (ec == 0) {break;}
		  else{
			  
			oled.text(0, 0,"Set Address = 0x%h",iKBAddr);
			oled.text(1, 0,"press SW_reset iKBz");
			oled.show();
			if ((millis()&0x0100)==0)
			  {
				sleds.setPixelColor(0,255,0,0);
				sleds.setPixelColor(1,255,0,0);
				sleds.setPixelColor(2,255,0,0);
				sleds.show();
				delay(5);
			  }
			  else
			  { sleds.setPixelColor(0,0,0,0);
				sleds.setPixelColor(1,0,0,0);
				sleds.setPixelColor(2,0,0,0);
				sleds.show();
		      }
		 }
		}
	}
	oled.clearDisplay();
	oled.show();
	sleds.setPixelColor(0,0,0,0);
	sleds.setPixelColor(1,0,0,0);
	sleds.setPixelColor(2,0,0,0);
	sleds.show();
	Wire.beginTransmission(iKBAddr);
    Wire.write(0);
    Wire.endTransmission();
	
}

void servo(uint8_t ch,int angle){
    angle = (angle > 200 ? 200 : angle);
    angle = (angle < -1 ? -1 : angle);
    Wire.beginTransmission(iKBAddr);
    Wire.write(0x40+(1 << (ch-10)));
    Wire.write(angle);
    Wire.endTransmission();
}

void motor(int8_t ch, uint8_t power) {
  if (ch > 0 && ch < 5) {
    Wire.beginTransmission(iKBAddr);
    Wire.write(0x20 | (1 << (ch - 1)));
    Wire.write(power);
    Wire.endTransmission();
  }
  else if (ch == 12) {
    Wire.beginTransmission(iKBAddr);
    Wire.write(0x23);
    Wire.write(power);
    Wire.endTransmission();
  }

}

void motor_stop(int8_t ch) {
  if (ch > 0 && ch < 5) {
    Wire.beginTransmission(iKBAddr);
    Wire.write(0x20 | (1 << (ch - 1)));
    Wire.write(0);
    Wire.endTransmission();
  }
  else if (ch == 12) {
    Wire.beginTransmission(iKBAddr);
    Wire.write(0x23);
    Wire.write(0);
    Wire.endTransmission();
  }
}

void ao(void) {
  Wire.beginTransmission(iKBAddr);
  Wire.write(0x23);
  Wire.write(0);
  Wire.endTransmission();
}

void fd(int8_t power) {
  power = (power > 100 ? 100 : power);
  power = (power < 0 ? 0 : power);
  Wire.beginTransmission(iKBAddr);
  Wire.write(0x23);
  Wire.write(power);
  Wire.endTransmission();
}

void bk(int8_t power) {
  power = (power > 100 ? 100 : power);
  power = (power < 0 ? 0 : power);
  Wire.beginTransmission(iKBAddr);
  Wire.write(0x23);
  Wire.write(-power);
  Wire.endTransmission();
}

void sl(int8_t power) {
  power = (power > 100 ? 100 : power);
  power = (power < 0 ? 0 : power);
  Wire.beginTransmission(iKBAddr);
  Wire.write(0x21);
  Wire.write(-power);
  Wire.endTransmission();
  Wire.beginTransmission(iKBAddr);
  Wire.write(0x22);
  Wire.write(power);
  Wire.endTransmission();
}

void sr(int8_t power) {
  power = (power > 100 ? 100 : power);
  power = (power < 0 ? 0 : power);
  Wire.beginTransmission(iKBAddr);
  Wire.write(0x21);
  Wire.write(power);
  Wire.endTransmission();
  Wire.beginTransmission(iKBAddr);
  Wire.write(0x22);
  Wire.write(-power);
  Wire.endTransmission();
}

void tl(int8_t power) {
  power = (power > 100 ? 100 : power);
  power = (power < 0 ? 0 : power);
  Wire.beginTransmission(iKBAddr);
  Wire.write(0x21);
  Wire.write(0);
  Wire.endTransmission();
  Wire.beginTransmission(iKBAddr);
  Wire.write(0x22);
  Wire.write(power);
  Wire.endTransmission();
}

void tr(int8_t power) {
  power = (power > 100 ? 100 : power);
  power = (power < 0 ? 0 : power);
  Wire.beginTransmission(iKBAddr);
  Wire.write(0x21);
  Wire.write(power);
  Wire.endTransmission();
  Wire.beginTransmission(iKBAddr);
  Wire.write(0x22);
  Wire.write(0);
  Wire.endTransmission();
}

int analog(uint8_t ch){
	if((ch>=10)&&(ch<=17)){
	ch = ch-10;	
    uint8_t data[2];
    Wire.beginTransmission(iKBAddr);
    Wire.write(0x80 + (ch << 4));
    Wire.endTransmission();
    Wire.requestFrom(iKBAddr, 2);
    if(Wire.available() == 2){
        data[0] = Wire.read();
        data[1] = Wire.read();
    }
    int raw_adc = ((data[0] & 0x0F) * 256) + data[1];
    return raw_adc;
	}else{
		return analogRead(ch);
	}
}
//ch =  i0 to i7 on iKBz , ch = 5,19,18,32,33,34,35,26 on ipst-wifi
int in(uint8_t ch){
	if((ch>=10)&&(ch<=17)){
	ch = ch-10;	
    uint8_t data;
    Wire.beginTransmission(iKBAddr);
    Wire.write(8 + ch);
    Wire.write(2);
    Wire.endTransmission();
    Wire.requestFrom(iKBAddr, 1);
    if(Wire.available() == 1) data = Wire.read();
    return data;
	}else{
	    pinMode(ch,INPUT_PULLUP);
	   return digitalRead(ch);
	}
}

void out(int8_t ch, bool state){
	if((ch>=10)&&(ch<=17)){
	ch = ch-10;		
    Wire.beginTransmission(iKBAddr);
    Wire.write(8 + ch);
    Wire.write(state);
    Wire.endTransmission();
	}else{
	  pinMode(ch,OUTPUT);
	  digitalWrite(ch,state);
	}
}

int knob(void)
{
  int __knobValue;
  __knobValue=analogRead(36);
  return(__knobValue);
}

int knob(int scale)
{
  long value;
  value=knob();
  value=((value*(scale))/4095);
  if (value>scale)
  {
     value=scale;
  }
  return(value);
}

int knob(int scaleCCW,int scaleCW)
{
  long value;
  value=knob();
  if (scaleCW>=scaleCCW)
  {
	value=value/(4095/((scaleCW+1)-scaleCCW));
	value+=scaleCCW;
	if (value>scaleCW){
	  value=scaleCW;
	}
  }
  else
  {
	value=4095-value;
	value=value/(4095/((scaleCCW+1)-scaleCW));
	value+=scaleCW;
	if (value>scaleCCW)
	{
	  value=scaleCCW;
	}
  }
  return(value);
}

//-------------------------------------------------------------
// End Andlog
//-------------------------------------------------------------

//-------------------------------------------------------------
// Switch A B
//-------------------------------------------------------------

int SW_1(void)
{
  pinMode(0,INPUT_PULLUP);
  if (digitalRead(0)==0)
  {
	return(1);
  }
  else
  {
	return(0);
  }
}

void waitSW_1(void)
{
  while(1)
  {
    pinMode(0,INPUT_PULLUP);
    if (digitalRead(0)!=0)
	{ if ((millis()&0x0100)==0)
	  {
		pinMode(18,OUTPUT);
		digitalWrite(18,LOW);
		delay(5);
	  }
	  else
	  { digitalWrite(18,HIGH);}
	}
	else
	{ pinMode(18,OUTPUT); 
	  digitalWrite(18,LOW);
	  pinMode(0,INPUT_PULLUP);
	  break;
	}
  }
}
/*void sound(int frequency, int duration) {
    ledcSetup(0, frequency, 8);
    ledcAttachPin(BUZZER_PIN, 0);
    ledcWrite(0, SOUND_ON);
    delay(duration);
    ledcWrite(0, SOUND_OFF);
 }
void beep(void)
{	
	sound(500,100);
}*/
void sled(uint16_t n, uint8_t r, uint8_t g, uint8_t b) {
      sleds.setPixelColor(n,r,g,b);
      sleds.show();
}
void sledFill(uint8_t r, uint8_t g, uint8_t b) {
	 for(int i=0;i<3;i++){
    // pixels.Color takes RGB values, from 0,0,0 up to 255,255,255
     sleds.setPixelColor(i,r,g,b);
     sleds.show();
     delay(1); // Delay for a period of time (in milliseconds).
  }    
}
void sledClear() {
	 for(int i=0;i<3;i++){
    // pixels.Color takes RGB values, from 0,0,0 up to 255,255,255
     sleds.setPixelColor(i,0,0,0);
     sleds.show();
     delay(1); // Delay for a period of time (in milliseconds).
  }    
}
void sled(uint16_t n, uint8_t r, uint8_t g, uint8_t b,uint8_t BRIGHTNESS) {
	  sleds.setBrightness(BRIGHTNESS);
      sleds.setPixelColor(n,r,g,b);
      sleds.show();
}
void sledBrightness(uint8_t BRIGHTNESS){
	  sleds.setBrightness(BRIGHTNESS);
}
