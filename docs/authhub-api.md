### Existing API

  * API Specification

    + All api result will be returned in format {'retbody': RETBODY, 'retcode': RETCODE}.

    + If api call finished successfully, RETCODE is 0, and retbody will be api response in
    json format

    + Else RETCODE is api's errocode, and RETBODY is error message.

    + For each api call, do not omit the back slash at the end, like **/v1/users** is not valid
    api path, but **/v1/users/** is valid

  * User Management

    + user create
        - Method: POST
        - URL: /v1/users/
        - Params:
          ```
          {
            'username': USERNAME,
            'password': PASSWORD,
            'type': USERTYPE(supervisor, bank or p2p)
          }
          ```
        - Return:
          ```
          {
            'id': USERID,
            'username': USERNAME,
            'type': UERTYPE,
            'created_at': CREATED_AT,
          }
          ```

    + user list
        - Method: GET
        - URL: /v1/users/
        - Return: TO BE UPDATED

    + user update
        - Method: PUT
        - URL: /v1/users/{user_id}/
        - Params:
        ```
          {
            'description': USER_DESCRIPTION,
            'phone': USER_PHONE,
            'email': USER_EMAIL
          }
        ```
        - Return: TO BE UPDATED

    + user detail
      - Method: GET
      - URL: /v1/users/{user_id}/
      - Return: TO BE UPDATED

    + user delete
      - Method: DELETE
      - URL: /v1/users/{user_id}/
      - Return: TO BE UPDATED

    + user reset password
      - Method: PUT
      - URL: /v1/users/{user_id}/reset_password/
      - Params: {'password': USER_PASSWORD}
      - Return: TO BE UPDATED

  * Toke Management

    + Token Generate
      - Method: POST
      - URL: /v1/tokens/
      - Params:
      ```
        {
          'username': USERNAME,
          'password': PASSWORD
        }
      ```
      - Return: TO BE UPDATED

    + Token revoke
      - Method: DELETE
      - URL: /v1/tokens/{token_id}/
      - Return: TO BE UPDATED

    + Token Check

      - Method: GET
      - URL: /v1/tokens/{token_id}/
      - Return: TO BE UPDATED

  * Role Management

    + Role Create
      - Method: POST
      - URL: /v1/roles/
      - Params:

        ```
        {
          'name': ROLE_NAME,
          'description': ROLE_DESCRIPTION
        }
        ```
      - Return: TO BE UPDATED

    + Role List
      - Method: GET
      - URL: /v1/roles/
      - Return: TO BE UPDATED

    + Role Detail
      - Method: GET
      - URL: /v1/roles/{role_id}/
      - Return: TO BE UPDATED

    + Role Update
      - Method: PUT
      - URL: /v1/roles/{role_id}/
      - Params:
        ```
        {
          'description': ROLE_DESCRIPTION
        }
        ```
      - Return: TO BE UPDATED

    + Role Delete

      - Method: DELETE
      - URL: /v1/roles/{role_id}/
      - Return: TO BE UPDATED

  * UserRole Management

    + User Role Grant
      - Method: POST
      - URL: /v1/users/{user_id}/roles/
      - Params: {'rolename': rolename}
      - Return: TO BE UPDATED

    + User Role List
      - Method: GET
      - URL: /v1/users/{user_id}/roles/
      - Return: TO BE UPDATED

    + User Role Revoke
      - Method: DELETE
      - URL: /v1/users/{user_id}/roles/{role_id}/
      - Return: TO BE UPDATED
