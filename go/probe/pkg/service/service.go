package service

import (
	"bufio"
	"encoding/json"
	"fmt"
	"github.com/preludeorg/detect-clients/go/probe/internal/hades"
	"github.com/preludeorg/detect-clients/go/probe/internal/util"
	"os"
	"strings"
)

type ProbeService struct {
	HQ            string
	Token         string
	AccountId     string
	AccountSecret string
	proc          *hades.Probe
}

type Actions interface {
	Start()
	Stop()
	Register(string)
	LoadKeychain()
}

func CreateService() *ProbeService {
	return &ProbeService{
		HQ:            util.GetEnv("PRELUDE_HQ", "https://detect.prelude.org"),
		Token:         util.GetEnv("PRELUDE_TOKEN", ""),
		AccountId:     util.GetEnv("PRELUDE_ACCOUNT_ID", ""),
		AccountSecret: util.GetEnv("PRELUDE_ACCOUNT_SECRET", ""),
		proc:          nil,
	}
}

func (ps *ProbeService) Start() {
	ps.proc = hades.CreateProbe(ps.Token, ps.HQ)
	go ps.proc.Start()
}

func (ps *ProbeService) Stop() {
	if ps.proc != nil {
		ps.proc.Stop()
	}
}

func (ps *ProbeService) Register(name ...string) error {
	var err error
	if len(name) < 1 {
		name = make([]string, 1)
		name[0], err = os.Hostname()
		if err != nil {
			return err
		}
	}
	api := fmt.Sprintf("%s/account/endpoint", ps.HQ)
	headers := map[string]string{"account": ps.AccountId, "token": ps.AccountSecret, "Content-Type": "application/json"}
	data, err := json.Marshal(map[string]string{"id": name[0]})
	resp, err := util.Post(api, data, headers)
	ps.Token = fmt.Sprintf("%s", resp)
	return nil
}

func (ps *ProbeService) LoadKeychain(path string) error {
	f, err := os.Open(path)
	if err != nil {
		return err
	}
	defer f.Close()
	section := false
	scanner := bufio.NewScanner(f)
	scanner.Split(bufio.ScanLines)
	for scanner.Scan() {
		line := scanner.Text()
		if strings.HasPrefix(line, "[") {
			section = strings.Contains(line, "default")
		}
		if section {
			if val := checkLine(line, "hq"); val != "" {
				ps.HQ = val
			} else if val = checkLine(line, "account"); val != "" {
				ps.AccountId = val
			} else if val = checkLine(line, "token"); val != "" {
				ps.AccountSecret = val
			}
		}
	}
	if err = scanner.Err(); err != nil {
		return err
	}
	return nil
}

func checkLine(line, key string) string {
	if strings.HasPrefix(line, key) {
		s := strings.SplitN(line, "=", 2)
		if len(s) == 2 {
			return strings.TrimSpace(s[1])
		}
	}
	return ""
}
