#include "Wire.h"


bool connectToGround = false;
int LightPin=2;

String command="";
word inputs=0x00;
const byte mergerAddress = 0x27;
const byte startAddress = 0x20;


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
    outputG = 0x00;
    bitSet(output, (channel-1)/8);
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
  Wire.begin();
  for ( byte address=0x20; address <= 0x27; ++address ) {
      initI2C(address);
  }
  disconnectBoard(false); 

  // Init the light
  pinMode(LightPin,OUTPUT);
  digitalWrite(LightPin,HIGH);

}

int keyAddress=-1;

void loop() {
 if (Serial.available()) {
    command = Serial.readStringUntil(' ');
    command.toUpperCase();
    if ( command.startsWith("RES") )  //RESet
    {
      Serial.println("I received: RESET");
      for ( byte address=0x20; address <= 0x27; ++address )
        initI2C(address);
      disconnectBoard(false);
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

    if ( command.startsWith("LIGHT") )  //TEST addr ch
    {
      String command2 = Serial.readStringUntil(' ');
      byte lightV = command2.toInt();
      if ( lightV == 0 ) {
        digitalWrite(LightPin,LOW); 
        Serial.println("Light OFF");
      }
      else if ( lightV == 1 ) {
        digitalWrite(LightPin,HIGH);
        Serial.println("Light ON");
      }
      else
        Serial.println("Usage: LIGHT 0/1"); 
    }
  }
  delay(100);
}
