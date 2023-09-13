package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strings"
)

type BearerToken struct {
	AccessToken string `json:"access_token"`
	ExpiresIn   int    `json:"expires_in"`
}

type CredentialBody struct {
	client_id     string
	client_secret string
	member_cid    string
}

type APIHarness struct {
	BaseURL        string
	CredentialBody *CredentialBody
	BearerToken    *BearerToken
}

func NewAPIHarness(baseURL string, clientID string, clientSecret string) *APIHarness {
	return &APIHarness{
		BaseURL: baseURL,
		CredentialBody: &CredentialBody{
			client_id:     clientID,
			client_secret: clientSecret,
		},
	}
}

func (h *APIHarness) GetBearerToken() error {
	if h.BearerToken == nil {
		return h.RefreshBearerToken()
	}
	if h.BearerToken.ExpiresIn < 60 {
		return h.RefreshBearerToken()
	}
	return nil
}

func (h *APIHarness) RefreshBearerToken() error {
	url := fmt.Sprintf("%s/oauth2/token", h.BaseURL)
	encodedBody := fmt.Sprintf("client_id=%s&client_secret=%s", h.CredentialBody.client_id, h.CredentialBody.client_secret)
	req, err := http.NewRequest("POST", url, strings.NewReader(encodedBody))
	if err != nil {
		return err
	}
	req.Header.Add("Content-Type", "application/x-www-form-urlencoded")
	req.Header.Add("Accept", "application/json")
	req.Header.Add("User-Agent", "falcon-go-sdk/1.0.0")
	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	bearerToken := &BearerToken{}
	if err := json.NewDecoder(resp.Body).Decode(bearerToken); err != nil {
		return err
	}
	h.BearerToken = bearerToken
	return nil
}

func (h *APIHarness) Get(path string) (*http.Response, error) {
	if err := h.GetBearerToken(); err != nil {
		return nil, err
	}
	url := fmt.Sprintf("%s%s", h.BaseURL, path)
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return nil, err
	}
	req.Header.Add("Authorization", fmt.Sprintf("Bearer %s", h.BearerToken.AccessToken))
	req.Header.Add("Accept", "application/json")
	req.Header.Add("User-Agent", "falcon-go-sdk/1.0.0")
	client := &http.Client{}
	return client.Do(req)
}

func (h *APIHarness) Post(path string, body string) (*http.Response, error) {
	if err := h.GetBearerToken(); err != nil {
		return nil, err
	}
	url := fmt.Sprintf("%s%s", h.BaseURL, path)
	req, err := http.NewRequest("POST", url, strings.NewReader(body))
	if err != nil {
		return nil, err
	}
	req.Header.Add("Authorization", fmt.Sprintf("Bearer %s", h.BearerToken.AccessToken))
	req.Header.Add("Content-Type", "application/json")
	req.Header.Add("Accept", "application/json")
	req.Header.Add("User-Agent", "falcon-go-sdk/1.0.0")
	client := &http.Client{}
	return client.Do(req)
}

func main() {
	harness := NewAPIHarness("https://api.crowdstrike.com", "8b410b9b7106432bb1f9bb6ec22ddd10", "ci4d5HCWgmX8fl9FSyUzt7TbDkp0Aq26R1ZneK3v")
	if err := harness.GetBearerToken(); err != nil {
		fmt.Println(err)
		fmt.Println("ERROR")
		return
	}
}
