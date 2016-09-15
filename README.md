# EAuth README

  EAuth provides pure RestAPI for user/group/role/token management.

### Get Started

[Get Started Guide](docs/get-started.md)

### APIs

[API Reference](docs/authhub-api.md)


### TODO

  * Django Exception Handling

    If user request for invalid api urls, like "v1/user/", django will raise Exception to return default exception page.  

    Need write django middleware to catch this exception and return exception with error message "invalid request path" back to user
