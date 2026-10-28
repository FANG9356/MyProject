package utils

import (
	"fmt"
	"strings"

	"github.com/sigurn/crc16"
)


func GeneratePromptPayPayload(targetID string, amount float64) string {

	targetID = strings.ReplaceAll(targetID, "-", "")
	targetID = strings.ReplaceAll(targetID, " ", "")

	if targetID == "" {
		return ""
	}

	var subTag string
	if len(targetID) == 10 && strings.HasPrefix(targetID, "0") {

		formattedPhone := "0066" + targetID[1:]
		subTag = fmt.Sprintf("01%02d%s", len(formattedPhone), formattedPhone)
	} else if len(targetID) >= 13 {

		subTag = fmt.Sprintf("02%02d%s", len(targetID), targetID)
	} else {

		subTag = fmt.Sprintf("01%02d%s", len(targetID), targetID)
	}


	subTag00 := "0016A000000677010111"
	tag29Val := subTag00 + subTag
	tag29 := fmt.Sprintf("29%02d%s", len(tag29Val), tag29Val)


	amountStr := fmt.Sprintf("%.2f", amount)
	tag54 := fmt.Sprintf("54%02d%s", len(amountStr), amountStr)


	payload := "000201010212" + tag29 + "5802TH5303764" + tag54 + "6304"


	table := crc16.MakeTable(crc16.CRC16_CCITT_FALSE)
	crc := crc16.Checksum([]byte(payload), table)


	return fmt.Sprintf("%s%04X", payload, crc)
}
