package main

import (
	"io"
	"os"
	"fmt"
	"flag"
	"bufio"
	"regexp"
	"net/url"
	"os/exec"
	"runtime"
	"net/http"
	"path/filepath"
)

var (
	PRELUDE_API *string
	PRELUDE_CA  *string
)

var re = regexp.MustCompile(`[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}`)

func loop(testID string, dat string) {
	dos := fmt.Sprintf("%s-%s", runtime.GOOS, runtime.GOARCH)

	req, err := http.NewRequest("GET", *PRELUDE_API, nil)
	if err != nil {
		fmt.Println("Verify your API is correct", err)
		return
	}

	req.Header.Set("token", os.Getenv("PRELUDE_TOKEN"))
	req.Header.Set("id", testID)
	req.Header.Set("dos", dos)
	req.Header.Set("dat", dat)
	req.Header.Set("version", "2")

	client := http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		fmt.Println("Failed retreiving test:", err)
		return
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		fmt.Println("Failed extracting test:", err)
		return
	}

	location := resp.Request.URL.String()
	test := re.FindString(location)

	if test != "" && test == testID {
		parsedURL, _ := url.Parse(location)

		if *PRELUDE_CA == parsedURL.Host {
			bin, _ := os.Executable()
			executable := filepath.Join(filepath.Dir(bin), *PRELUDE_CA, test)
			os.WriteFile(executable, body, 0755)

			cmd := exec.Command(executable)
			cmd.Stdout = os.Stdout
			cmd.Stderr = os.Stderr
			cmd.Run()

			if cmd.ProcessState != nil {
				code := cmd.ProcessState.ExitCode()
				dat = fmt.Sprintf("%s:%d", test, code)
				loop("", dat)
			}

		} else {
			fmt.Println("Invalid CA ", parsedURL.Host)
		}
	}
}

func main() {
	PRELUDE_API = flag.String("API", "https://api.us2.preludesecurity.com", "Detect API")
	PRELUDE_CA = flag.String("CA", "prelude-account-us2-us-east-1.s3.amazonaws.com", "Detect certificate authority")
	flag.Parse()
	
	fmt.Println("[P] Detect API:", *PRELUDE_API)
	fmt.Println("[P] Detect CA:", *PRELUDE_CA)

	os.Mkdir(*PRELUDE_CA, 0755)
	scanner := bufio.NewScanner(os.Stdin)

	if os.Getenv("PRELUDE_TOKEN") == "" {
		fmt.Print("[P] Enter a PRELUDE_TOKEN: ")
		scanner.Scan()
		os.Setenv("PRELUDE_TOKEN", scanner.Text())
	}

	for {
		fmt.Print("[P] Enter a test ID: ")
		scanner.Scan()
		testID := scanner.Text()
		if testID != "" {
			loop(testID, "")
		}
	}
}