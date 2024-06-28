package core

import (
	"errors"
	"os"
	"path/filepath"
	"sync"

	"github.com/mitchellh/go-homedir"
	"github.com/spf13/cobra"
	"github.com/spf13/viper"

	"portal/libs/logger"
)

const (
	activeProfileKey string = "activeProfile"
)

var (
	initMutex = sync.Mutex{}
)

type Config struct {
	Api        string `mapstructure:"api"`
	Secret     string `mapstructure:"secret"`    // Secret is used for m2m flow
	ClientID   string `mapstructure:"client_id"` // The ClientID is used for the user login flow
	DevMode    bool   `mapstructure:"dev_mode"`
	AuthUrl    string `mapstructure:"auth_url"`
	HomeFolder string `mapstructure:"home_folder"`
}

func GetActiveProfile() string {
	profile, set := lookupEnv("PROFILE")
	if set {
		return profile
	}
	return viper.GetString(activeProfileKey)
}

// func GetActiveProfile() string {
// 	return "portal-profile" // Profiles is currently not yet a thing
// }

func CurrentConfigValid() bool {
	config := GetCurrentConfig()
	if config.Api == "" || config.ClientID == "" || config.Secret == "" || config.AuthUrl == "" {
		return false
	}
	return true
}

func DefaultConfig() Config {
	return Config{
		DevMode: false,
	}
}

func InitConfig() {
	// Avoid concurrent initialization during tests
	initMutex.Lock()
	defer initMutex.Unlock()

	loc := cliLocation()
	viper.AddConfigPath(loc)
	viper.SetConfigName("profiles")
	viper.SetConfigType("toml")
	viper.SetDefault("activeProfile", "default")

	var configFileNotFoundError viper.ConfigFileNotFoundError
	if err := viper.ReadInConfig(); err != nil && !errors.As(err, &configFileNotFoundError) {
		panic(err)
	}

	writeViper()
}
func EnsureValidConfig(cmd *cobra.Command, args []string) {
	if cmd.Use != "configure" && !CurrentConfigValid() {
		logger.Errorf("Please set up a default configuration with at least a single OIDC host, run portal auth configure -h for extra information")
		os.Exit(1)
	}
}

func writeViper() {
	EnsureConfigDirectoryExists()
	if err := viper.WriteConfig(); err != nil {
		var configFileNotFoundError viper.ConfigFileNotFoundError
		if errors.As(err, &configFileNotFoundError) {
			if err = viper.SafeWriteConfig(); err != nil {
				logger.Errorf("Ran into an error when safe writing the config")
				panic(err)
			}
		} else {
			logger.Errorf("Ran into an error when writing the config")
			panic(err)
		}
	}
}

func cliLocation() string {
	home, err := homedir.Dir()
	if err != nil {
		panic(err)
	}
	return filepath.Join(home, ".portal")
}

func lookupEnv(envVariable string) (string, bool) {
	env, ok := viper.Get(envVariable).(string) //os.LookupEnv(fmt.Sprintf("OIDC_%s", envVariable))

	if !ok {
		return "", false
	}
	return env, true
}

func ChangeActiveProfile(newActiveProfile string) {
	switch {
	case viper.GetString(activeProfileKey) == newActiveProfile:
		logger.Infof("'%s' already is the active profile", newActiveProfile)
	case newActiveProfile == "default":
		viper.Set(activeProfileKey, newActiveProfile)
		writeViper()
		logger.Infof("Switched active profile to '%s'", newActiveProfile)
	case !viper.InConfig(newActiveProfile):
		logger.Errorf("'%s' is not a valid profile", newActiveProfile)
	default:
		viper.Set(activeProfileKey, newActiveProfile)
		writeViper()
		logger.Infof("Switched active profile to '%s'", newActiveProfile)
	}
}

func EnsureConfigDirectoryExists() {
	loc := cliLocation()
	if _, err := os.Stat(loc); os.IsNotExist(err) {
		if err = os.MkdirAll(loc, 0755); err != nil {
			logger.Errorf("Ran into an error when creating the configuration directory with location: %s", loc)
			panic(err)
		}
	}
}

func GetCurrentConfig() Config {
	var config = DefaultConfig()
	activeProfile := GetActiveProfile()
	if err := viper.UnmarshalKey(activeProfile, &config); err != nil {
		panic(err)
	}
	// viper.AddConfigPath("../")
	// viper.SetConfigName(".prod")
	//viper.SetConfigFile("../.env")
	err := viper.ReadInConfig()
	if err != nil {
		panic("Config not read")
	}

	api, set := lookupEnv("api")
	if set {
		config.Api = api
	}
	secret, set := lookupEnv("secret")
	if set {
		config.Secret = secret
	}
	client, set := lookupEnv("client_id")
	if set {
		config.ClientID = client
	}
	auth, set := lookupEnv("auth_url")
	if set {
		config.AuthUrl = auth
	}
	return config
}

func configToViper(config Config, activeProfile string) {
	viper.Set(activeProfile, map[string]string{
		"api":       config.Api,
		"auth_url":  config.AuthUrl,
		"secret":    config.Secret,
		"client_id": config.ClientID,
	})
}

// WriteConfig This writes the config to the toml file
// This does not update the token, use the writeToken method for that.
func WriteConfig(config Config, activeProfile string) {
	configToViper(config, activeProfile)
	writeViper()
}
