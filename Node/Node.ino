#include "DHT.h"
#define DHTPIN 3    
#define DHTTYPE DHT11   // DHT 11 
DHT dht(DHTPIN, DHTTYPE);
#include <SPI.h> //Import SPI librarey 
#include <RH_RF95.h> // RF95 from RadioHead Librarey 


#define RFM95_CS 10 //CS if Lora connected to pin 10
#define RFM95_RST 9 //RST of Lora connected to pin 9
#define RFM95_INT 2 //INT of Lora connected to pin 2

// Change to 434.0 or other frequency, must match RX's freq!
#define RF95_FREQ 434.0

// Singleton instance of the radio driver
RH_RF95 rf95(RFM95_CS, RFM95_INT);
int temp,hum;
void setup() 
{
  Serial.println("DHTxx test!");
   dht.begin();
  Serial.begin(9600);
  
  pinMode(RFM95_RST, OUTPUT); 
  digitalWrite(RFM95_RST, LOW);
  delay(10);
  digitalWrite(RFM95_RST, HIGH);
  delay(10);

  while (!rf95.init()) {
    Serial.println("LoRa radio init failed");
    while (1);
  }
  

  if (!rf95.setFrequency(RF95_FREQ)) {
    Serial.println("setFrequency failed");
    while (1);
  }

  rf95.setTxPower(18); 
}

void loop()
{
  temp = dht.readTemperature();
  hum = dht.readHumidity();
String humidity = String(hum); //int to String
String temperature = String(temp);
String data = temperature +"@"+ humidity;
char d[5];
data.toCharArray(d, 5); //String to char array
rf95.send(d, sizeof(d));
rf95.waitPacketSent();
delay(5000);
  
  if (isnan(temp) || isnan(hum)) {
    Serial.println("Failed to read from DHT");
  } else {
    Serial.print("do_am: "); 
    Serial.print(hum);
    Serial.print(" %\t");
    Serial.print("nhiet_do: "); 
    Serial.print(temp);
    Serial.println(" *C");

  }

}
