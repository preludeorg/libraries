package hades

import (
	"encoding/hex"
	"fmt"
	"github.com/preludeorg/detect-clients/go/probe/internal/util"
	"math"
	"os"
	"os/exec"
	"runtime"
	"strconv"
	"time"
)

type Probe struct {
	signals chan bool
	token   string
	hq      string
	dos     string
	sleep   time.Duration
	cwd     string
}

type Actions interface {
	Start()
	Stop()
	runTask([]byte)
	run(string) int
	save([]byte) (*os.File, error)
}

func CreateProbe(token, hq string) *Probe {
	wd, err := util.FindWorkingDirectory()
	if err != nil {
		panic(err)
	}
	return &Probe{
		signals: make(chan bool),
		token:   token,
		hq:      hq,
		dos:     fmt.Sprintf("%s-%s.exe", runtime.GOOS, runtime.GOARCH),
		sleep:   43200 * time.Second,
		cwd:     wd,
	}
}

func (p *Probe) Start() {
	for {
		p.runTask([]byte(p.dos))
		select {
		case <-p.signals:
			return
		case <-time.After(p.sleep):
			continue
		}
	}
}

func (p *Probe) Stop() {
	p.signals <- true
}

func (p *Probe) runTask(data []byte) {
	if resp, err := util.Request(fmt.Sprintf("%s", p.hq), data, map[string]string{"token": p.token, "Content-Type": "application/x-www-form-urlencoded"}); err == nil && len(resp) > 36 {
		id := resp[:36]
		exe, err := p.save(resp[36:])
		if err == nil {
			result := p.run(exe)
			_ = os.Remove(exe.Name())
			p.runTask([]byte(fmt.Sprintf("%s:%s:%d", p.dos, id, result)))
		}
	}
}

func (p *Probe) save(data []byte) (*os.File, error) {
	f, err := os.CreateTemp(p.cwd, "detect")
	if err != nil {
		return nil, err
	}

	decoded, err := hex.DecodeString(string(data))
	if err != nil {
		return nil, err
	}

	if _, err := f.Write(decoded); err != nil {
		return nil, err
	}

	if err := f.Close(); err != nil {
		return nil, err
	}

	err = os.Chmod(f.Name(), 0500)
	if err != nil {
		return nil, err
	}

	return f, nil
}

func (p *Probe) run(exe *os.File) int {
	test, err := exec.Command(exe.Name(), "test").Output()
	if err != nil {
		return 3
	}
	cleanup, err := exec.Command(exe.Name(), "cleanup").Output()
	if err != nil {
		return 4
	}
	testVal, err := strconv.ParseFloat(fmt.Sprintf("%s", test), 64)
	if err != nil {
		return 3
	}
	cleanupVal, err := strconv.ParseFloat(fmt.Sprintf("%s", cleanup), 64)
	if err != nil {
		return 4
	}
	return int(math.Max(testVal, cleanupVal))
}
