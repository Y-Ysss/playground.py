// CLI Mock Application

package main

import (
	"flag"
	"fmt"
	"time"
)

func main() {
	pathCmd := flag.String("f", "File Path", "File path")
	boolPtr := flag.Bool("b", false, "Timer")
	flag.Parse()
	fmt.Println(*pathCmd)
	if *boolPtr {
		fmt.Println("Timer")
		for i := 0; i < 10; i++ {
			time.Sleep(time.Second)
			fmt.Println(i)
		}
	}
	fmt.Println("Finished")
}
