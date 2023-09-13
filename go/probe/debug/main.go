package main

import (
	"bufio"
	"bytes"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"runtime"
)

var (
	PRELUDE_API *string
	PRELUDE_CA  *string
	HOSTNAME    *string
)

var re = regexp.MustCompile(`[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}`)

func executable(test string) string {
	bin, _ := os.Executable()
	executable := filepath.Join(filepath.Dir(bin), *PRELUDE_CA, test)

	if runtime.GOOS == "windows" {
		return executable + ".exe"
	}
	return executable
}

// In: 		TBD
// Out: 	The identifier of the current Falcon prevention policy
// Group: 	Alex, Mahina, James
func getPreventionPolicy() {
	// todo
}

// In:		An identifier for the policy to set
// Out:		A result that indicates whether the policy was applied
// Group:	Alex, Mahina, James
func setPreventionPolicy() {
	// todo
}

// done:	This struct will hold the test identifier and a collection of
//
//	structs that contain the timestamp for when the test was run
//	and the result code (e.g., 101, 127).
//
// Group:	Kenrick, Stephan
// PolicyResult struct will hold the test ID and a collection of evaluations
type Result struct {
	TestID      string       `json:"test_id"`
	Evaluations []Evaluation `json:"evaluations"`
}

// Evaluation struct will hold the policy name and the result code
type Evaluation struct {
	Policy string `json:"policy"`
	Code   int    `json:"code"`
}

// In:		Object/struct containing the results of the tests
// Out: 	A formatted table printed to stdout
// Group:	Kenrick, Stephan
func printResultTable(pr Result) {
	fmt.Println("Test ID: ", pr.TestID)
	fmt.Println("Policy\t\tCode")
	fmt.Println("------\t\t------")
	for _, evaluation := range pr.Evaluations {
		fmt.Printf("%s\t\t%d\n", evaluation.Policy, evaluation.Code)
	}
}

func loop(testID string, dat string, pr *Result) {
	// todo: 	Rewrite this function to iterate over each policy
	// 			and return a struct containing results and timestamps
	// 			Consider that after the request to pull the test down,
	// 			it is in memory and fair game for detection/prevention
	// Group:	Robin, Waseem

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
			executable := executable(test)
			os.WriteFile(executable, body, 0755)

			_, err := os.Stat(executable)
			if err == nil {
				cmd := exec.Command(executable)
				cmd.Stdout = os.Stdout
				cmd.Stderr = os.Stderr
				cmd.Run()

				if cmd.ProcessState != nil {
					code := cmd.ProcessState.ExitCode()
					pr.Evaluations = append(pr.Evaluations, Evaluation{Policy: "policy1", Code: code})
					// todo: Add this exit code to the collection of results
					loop("", fmt.Sprintf("%s:%d", test, code), pr)
				}
			} else if os.IsNotExist(err) {
				fmt.Println("[P] Test was quarantined (quickly)")
				loop("", fmt.Sprintf("%s:127", test), pr)
			}

		} else {
			fmt.Println("Invalid CA ", parsedURL.Host)
		}
	}
}

func registerEndpoint(accountID string, token string) {
	hostname := *HOSTNAME
	if hostname == "" {
		hostname, _ = os.Hostname()
	}
	jsonData, err := json.Marshal(map[string]string{
		"id": fmt.Sprintf("%s:%s", hostname, "0"),
	})

	req, err := http.NewRequest("POST", fmt.Sprintf("%s/detect/endpoint", *PRELUDE_API), bytes.NewBuffer(jsonData))
	if err != nil {
		fmt.Println("Failed to establish request:", err)
		return
	}
	req.Header.Set("account", accountID)
	req.Header.Set("token", token)

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		fmt.Println("Error registering endpoint:", err)
		return
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if resp.StatusCode == http.StatusOK {
		os.Setenv("PRELUDE_TOKEN", string(body))
		return
	}
	fmt.Println(string(body))
	os.Exit(1)
}

func main() {
	PRELUDE_API = flag.String("api", "https://api.preludesecurity.com", "Detect API")
	PRELUDE_CA = flag.String("ca", "prelude-account-us1-us-east-2.s3.amazonaws.com", "Detect certificate authority")
	HOSTNAME = flag.String("host", "", "Hostname associated to this probe")

	flag.Parse()
	os.Mkdir(*PRELUDE_CA, 0755)

	var account, token string
	fmt.Print("[P] Enter account ID: ")
	fmt.Scanln(&account)
	fmt.Print("[P] Enter account token: ")
	fmt.Scanln(&token)
	registerEndpoint(account, token)

	fmt.Print("\n\n----- AUTHORIZED AND READY TO RUN TESTS -----\n\n")
	scanner := bufio.NewScanner(os.Stdin)

	for {
		fmt.Print("[P] Enter a test ID: ")
		scanner.Scan()
		testID := scanner.Text()

		pr := Result{
			TestID:      testID,
			Evaluations: make([]Evaluation, 0),
		}

		if testID != "" {
			loop(testID, "", &pr)
		}

		printResultTable(pr)
	}
}
