package main

import (
	"io"
	"os"
	"fmt"
	"bufio"
	"regexp"
	"net/url"
	"os/exec"
	"runtime"
	"net/http"
	"path/filepath"
)

const (
	PRELUDE_API   = "https://api.us2.preludesecurity.com"
	PRELUDE_CA    = "prelude-account-us2-us-east-1.s3.amazonaws.com"
)

var re = regexp.MustCompile(`[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}`)

func loop(test_id string, dat string) {
	dos := fmt.Sprintf("%s-%s", runtime.GOOS, runtime.GOARCH)

	req, err := http.NewRequest("GET", PRELUDE_API, nil)
	if err != nil {
		fmt.Println("Error creating request:", err)
		return
	}

	req.Header.Set("token", os.Getenv("PRELUDE_TOKEN"))
	req.Header.Set("id", test_id)
	req.Header.Set("dos", dos)
	req.Header.Set("dat", dat)
	req.Header.Set("version", "2")

	client := http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		fmt.Println("Error sending request:", err)
		return
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		fmt.Println("Error reading response:", err)
		return
	}

	location := resp.Request.URL.String()
	test := re.FindString(location)

	if test != "" {
		parsedURL, _ := url.Parse(location)

		if PRELUDE_CA == parsedURL.Host {
			os.WriteFile(test, body, 0755)
			bin, _ := os.Executable()
			executable := filepath.Join(filepath.Dir(bin), test)

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
			fmt.Println("Error: Invalid CA ", parsedURL.Host)
		}
	}
}

func main() {
	scanner := bufio.NewScanner(os.Stdin)

	if os.Getenv("PRELUDE_TOKEN") == "" {
		fmt.Print("[P] Please provide a PRELUDE_TOKEN: ")
		scanner.Scan()
		os.Setenv("PRELUDE_TOKEN", scanner.Text())
	}

	for {
		fmt.Print("[P] Enter test ID: ")
		scanner.Scan()
		testID := scanner.Text()

		if testID != "" {
			loop(testID, "")
		}
	}
}