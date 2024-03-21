#include <Adafruit_GFX.h>
#include "Adafruit_SSD1306.h"
#include "Wire.h"
#include <OnewireKeypadNM.h>

#define OLED_RESET LED_BUILTIN  //4
Adafruit_SSD1306 display(OLED_RESET);

#if (SSD1306_LCDHEIGHT != 64)
#error("Height incorrect, please fix Adafruit_SSD1306.h!");
#endif

bool connectToGround = false;

String command="";
word inputs=0x00;
const byte mergerAddress = 0x27;
const byte startAddress = 0x20;

char KEYS[]= {
  '1','2','3',
  '4','5','6',
  '7','8','9',
  '*','0','#',
};

int MINADC[]= {
  1015, 970, 900,
  750, 700, 651,
  580, 550, 501,
  470, 460, 400
};

int MAXADC[]= {
  1025, 1014, 969,
  899, 749, 699,
  650, 579, 549,
  500, 469, 459
};

OnewireKeypadNM < 12 > Keypad(Serial, KEYS, MINADC, MAXADC, 17, false);

const int MAX_KEYS=10;
char keyInserted[MAX_KEYS];
int keystroke_i=0; 

int processKeyPressed(const char key) {
 if (key=='#'){
    // Clear the buffer.
    display.clearDisplay();
    display.setTextSize(2);
    display.setTextColor(WHITE);
    display.setCursor(0,0);
    display.println(keyInserted);
    display.display();
    
    Serial.println(keyInserted);
    keystroke_i=0;
    return atoi(keyInserted);
  }
  else if(key == '*') {
    if ( keystroke_i>0 ) keyInserted[--keystroke_i] = '\0';
    display.clearDisplay();
    display.setTextSize(2);
    display.setTextColor(WHITE);
    display.setCursor(0,0);
    display.println(keyInserted);
    display.display();
    Serial.println(keyInserted);
  }
  else if(key!=NO_KEY) {
    keyInserted[keystroke_i] = key;
    
     // Clear the buffer.
    display.clearDisplay();
    display.setTextSize(2);
    display.setTextColor(WHITE);
    display.setCursor(0,0);
    ++keystroke_i;
    keyInserted[keystroke_i] = '\0';
    display.println(keyInserted);
    display.display();
    Serial.println(keyInserted);
  }
  return -1;
}



void initI2C(const byte& addr)
{
  Wire.beginTransmission(addr);
  Wire.write(0x00); // IODIRA register
  Wire.write(0x00); // set all of bank A to outputs
  Wire.endTransmission();
  Wire.beginTransmission(addr);
  Wire.write(0x01); // IODIRB register
  Wire.write(0x00); // set all of bank B to outputs
  Wire.endTransmission();
  setOutput(0,0,addr);  //set all outputs to 0x00
}

void sendByte(const word& data, const word& reg, const byte& addr)
{
  Wire.beginTransmission(addr);
  Wire.write(reg);
  Wire.write(data);
  Wire.endTransmission();
}

void setOutput(const word& dataA, const word& dataB, const byte& addr)
{
  sendByte( dataA, 0x12, addr );  // GPIOA
  sendByte( dataB, 0x13, addr );  // GPIOB
}

void disconnectBoard(const bool ground=false, const byte& address=0)
{
  byte defaultStatus = 0x00;  // 0x00 to have all disconnected at startup, 0xFF to have all grounded
  if (ground) defaultStatus = 0xFF;
  if (address==0)
  {
    for (byte add=0x20; add<=mergerAddress; ++add)
      setOutput( defaultStatus, 0, add );
  }
  else if (address>=0x20 && address<=0x27)
  {
    setOutput( defaultStatus, 0, address);
  }
  delay(500);
}

void setChannel(const byte& channel, const bool ground=false)
{
  disconnectBoard(ground);
  if ( channel >0 && channel <=32 )
  {
    byte channelOfBoard = (channel-1)%8;
    byte addressOfBoard = 0x20 + (channel-1)/8;
    byte output = 0x00;
    byte outputG = 0x00;
    bitSet(output, channelOfBoard);
    if (ground)
      outputG = ~output;
    setOutput( outputG, output, addressOfBoard );
    output = 0x00;
    bitSet(output, addressOfBoard);
    if (ground)
      outputG = ~output;
    setOutput( outputG, output, mergerAddress );
//    Serial.print("Connecting board ");
//    Serial.println(mergerAddress, HEX);
//    Serial.println(output, HEX);
  }
}


void setup() {
  Serial.begin(9600);
  display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  for ( byte address=0x20; address <= 0x27; ++address )
      initI2C(address);
  disconnectBoard(false);

  // Init the display
  display.clearDisplay();
  display.setTextSize(2);
  display.setTextColor(WHITE);
  display.setCursor(0,32);
  display.println("KU-CMS");
  display.display();

}

int keyAddress=-1;

void loop() {
 char key = Keypad.Getkey();
 
 if (keystroke_i>MAX_KEYS-1) {
    keystroke_i=0;
    keyAddress=-1;
 }
 if (keystroke_i==0) {
    //display.clearDisplay();
    display.clearUpperDisplay();
    display.setTextSize(1);
    display.setTextColor(WHITE);
    display.setCursor(0,0);
    display.println("Insert channel:");
    display.println("0 -> 32");
    display.display();
 }
 int keyChannel = processKeyPressed(key);
 if ( keyChannel != -1 ) {
  Serial.print("Received channel: ");
  Serial.println( keyChannel );
  if ( keyChannel >= 0 && keyChannel <= 32 ) {
      setChannel(keyChannel, connectToGround);
      Serial.print("I received: TEST ");
      Serial.println(keyChannel);
      display.setTextSize(1);
      display.setTextColor(WHITE);
      display.setCursor(0,32);
      display.println("Active channel:");
      display.println(keyChannel);
      display.display();
  }      
 }

 if (Serial.available()) {
    command = Serial.readStringUntil(' ');
    command.toUpperCase();
    if ( command.startsWith("RES") )  //RESet
    {
      Serial.println("I received: RESET");
      for ( byte address=0x20; address <= 0x27; ++address )
        initI2C(address);
      disconnectBoard(false);
      // Init the display
      display.clearDisplay();
      display.setTextSize(2);
      display.setTextColor(WHITE);
      display.setCursor(0,32);
      display.println("KU-CMS");
      display.display();
    }

    if ( command.startsWith("TEST") )  //TEST addr ch
    {
      String command2 = Serial.readStringUntil(' ');
      byte channel = command2.toInt();
      if ( channel >=0 && channel <=32 )
      {
        setChannel(channel,connectToGround);
        Serial.print("I received: TEST ");
        Serial.println(channel, HEX);
        display.clearLowerDisplay();
        display.setTextSize(1);
        display.setTextColor(WHITE);
        display.setCursor(0,32);
        display.println("Active channel:");
        display.println(channel);
        display.display();
      }
      else
        Serial.println("Usage: TEST channel[0-32]"); 
    }

    if ( command.startsWith("GND") )  //TEST addr ch
    {
      String command2 = Serial.readStringUntil(' ');
      byte groundV = command2.toInt();
      if ( groundV == 0 ) {
        connectToGround = false;
        Serial.print("All non selected channels will NOT be connected to GND ");
      }
      else if ( groundV == 1 ) {
        connectToGround = true;
        Serial.print("All non selected channels will be connected to GND ");
      }
      else
        Serial.println("Usage: GND 0 to not connect other channels to GND, GND 1 to connect them"); 
    }
  }
  delay(100);
}
