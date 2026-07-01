export type SuccessFullRegistrationResponse = {
    username: string;
}

export type RegisterRequest = {
    username: string;
    email: string;
    password: string;
    date_of_birth: string;
    name: string;
    surname: string;
}

export type LogInResponse = {
  access_token: string | null;
  username: string;
};

export type LogInRequest = {
    email: string;
    password: string;
}

export type UserInfo = {
  user_id: string;
  username: string | null;
  email: string | null;
  date_of_birth: string;
  name: string | null;
  surname: string | null;
  user_classification: string | null;
  api_keys: {
    has_pinecone_api_key: boolean;
    has_gemini_api_key: boolean;
    has_groq_api_key: boolean;
    has_mistral_api_key: boolean;
    has_cohere_api_key: boolean;
    has_jina_api_key: boolean;
  };
};


export type RefreshTokenResponse = {
  access_token: string;
  username: string;
};

export type RefreshTokenRequest = {
  access_token: string;
};


export type LogOutRequest= {
  access_token: string;
};

export type UpdateUserKeyRequest = {
                key_type: string;
                api_key: string;
}

export type DeleteUserKeyRequest = {
                key_type: string;
}