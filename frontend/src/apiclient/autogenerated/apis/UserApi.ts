/* tslint:disable */
/* eslint-disable */
/**
 *
 * No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)
 *
 * The version of the OpenAPI document: 0.0.0
 *
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 */

import * as runtime from "../runtime";
import {
  PaginatedUserListList,
  PaginatedUserListListFromJSON,
  PaginatedUserListListToJSON,
  UserCreate,
  UserCreateFromJSON,
  UserCreateToJSON,
  UserRetrieve,
  UserRetrieveFromJSON,
  UserRetrieveToJSON,
  UserToken,
  UserTokenFromJSON,
  UserTokenToJSON,
  UserUpdate,
  UserUpdateFromJSON,
  UserUpdateToJSON,
} from "../models";

export interface UserApiV2CreateRequest {
  userCreate: UserCreate;
}

export interface UserApiV2DestroyRequest {
  id: number;
}

export interface UserApiV2ListRequest {
  ordering?: string;
  page?: number;
  search?: string;
}

export interface UserApiV2RetrieveRequest {
  id: number;
}

export interface UserApiV2TokenCreateRequest {
  userToken?: UserToken;
}

export interface UserApiV2UpdateRequest {
  id: number;
  userUpdate: UserUpdate;
}

/**
 *
 */
export class UserApi extends runtime.BaseAPI {
  /**
   */
  async userApiV2CreateRaw(
    requestParameters: UserApiV2CreateRequest,
    initOverrides?: RequestInit
  ): Promise<runtime.ApiResponse<UserCreate>> {
    if (
      requestParameters.userCreate === null ||
      requestParameters.userCreate === undefined
    ) {
      throw new runtime.RequiredError(
        "userCreate",
        "Required parameter requestParameters.userCreate was null or undefined when calling userApiV2Create."
      );
    }

    const queryParameters: any = {};

    const headerParameters: runtime.HTTPHeaders = {};

    headerParameters["Content-Type"] = "application/json";

    if (
      this.configuration &&
      (this.configuration.username !== undefined ||
        this.configuration.password !== undefined)
    ) {
      headerParameters["Authorization"] =
        "Basic " +
        btoa(this.configuration.username + ":" + this.configuration.password);
    }
    if (this.configuration && this.configuration.apiKey) {
      headerParameters["Authorization"] =
        this.configuration.apiKey("Authorization"); // tokenAuth authentication
    }

    const response = await this.request(
      {
        path: `/user/api/v2/`,
        method: "POST",
        headers: headerParameters,
        query: queryParameters,
        body: UserCreateToJSON(requestParameters.userCreate),
      },
      initOverrides
    );

    return new runtime.JSONApiResponse(response, (jsonValue) =>
      UserCreateFromJSON(jsonValue)
    );
  }

  /**
   */
  async userApiV2Create(
    requestParameters: UserApiV2CreateRequest,
    initOverrides?: RequestInit
  ): Promise<UserCreate> {
    const response = await this.userApiV2CreateRaw(
      requestParameters,
      initOverrides
    );
    return await response.value();
  }

  /**
   */
  async userApiV2DestroyRaw(
    requestParameters: UserApiV2DestroyRequest,
    initOverrides?: RequestInit
  ): Promise<runtime.ApiResponse<void>> {
    if (requestParameters.id === null || requestParameters.id === undefined) {
      throw new runtime.RequiredError(
        "id",
        "Required parameter requestParameters.id was null or undefined when calling userApiV2Destroy."
      );
    }

    const queryParameters: any = {};

    const headerParameters: runtime.HTTPHeaders = {};

    if (
      this.configuration &&
      (this.configuration.username !== undefined ||
        this.configuration.password !== undefined)
    ) {
      headerParameters["Authorization"] =
        "Basic " +
        btoa(this.configuration.username + ":" + this.configuration.password);
    }
    if (this.configuration && this.configuration.apiKey) {
      headerParameters["Authorization"] =
        this.configuration.apiKey("Authorization"); // tokenAuth authentication
    }

    const response = await this.request(
      {
        path: `/user/api/v2/{id}/`.replace(
          `{${"id"}}`,
          encodeURIComponent(String(requestParameters.id))
        ),
        method: "DELETE",
        headers: headerParameters,
        query: queryParameters,
      },
      initOverrides
    );

    return new runtime.VoidApiResponse(response);
  }

  /**
   */
  async userApiV2Destroy(
    requestParameters: UserApiV2DestroyRequest,
    initOverrides?: RequestInit
  ): Promise<void> {
    await this.userApiV2DestroyRaw(requestParameters, initOverrides);
  }

  /**
   */
  async userApiV2ListRaw(
    requestParameters: UserApiV2ListRequest,
    initOverrides?: RequestInit
  ): Promise<runtime.ApiResponse<PaginatedUserListList>> {
    const queryParameters: any = {};

    if (requestParameters.ordering !== undefined) {
      queryParameters["ordering"] = requestParameters.ordering;
    }

    if (requestParameters.page !== undefined) {
      queryParameters["page"] = requestParameters.page;
    }

    if (requestParameters.search !== undefined) {
      queryParameters["search"] = requestParameters.search;
    }

    const headerParameters: runtime.HTTPHeaders = {};

    if (
      this.configuration &&
      (this.configuration.username !== undefined ||
        this.configuration.password !== undefined)
    ) {
      headerParameters["Authorization"] =
        "Basic " +
        btoa(this.configuration.username + ":" + this.configuration.password);
    }
    if (this.configuration && this.configuration.apiKey) {
      headerParameters["Authorization"] =
        this.configuration.apiKey("Authorization"); // tokenAuth authentication
    }

    const response = await this.request(
      {
        path: `/user/api/v2/`,
        method: "GET",
        headers: headerParameters,
        query: queryParameters,
      },
      initOverrides
    );

    return new runtime.JSONApiResponse(response, (jsonValue) =>
      PaginatedUserListListFromJSON(jsonValue)
    );
  }

  /**
   */
  async userApiV2List(
    requestParameters: UserApiV2ListRequest = {},
    initOverrides?: RequestInit
  ): Promise<PaginatedUserListList> {
    const response = await this.userApiV2ListRaw(
      requestParameters,
      initOverrides
    );
    return await response.value();
  }

  /**
   */
  async userApiV2RetrieveRaw(
    requestParameters: UserApiV2RetrieveRequest,
    initOverrides?: RequestInit
  ): Promise<runtime.ApiResponse<UserRetrieve>> {
    if (requestParameters.id === null || requestParameters.id === undefined) {
      throw new runtime.RequiredError(
        "id",
        "Required parameter requestParameters.id was null or undefined when calling userApiV2Retrieve."
      );
    }

    const queryParameters: any = {};

    const headerParameters: runtime.HTTPHeaders = {};

    if (
      this.configuration &&
      (this.configuration.username !== undefined ||
        this.configuration.password !== undefined)
    ) {
      headerParameters["Authorization"] =
        "Basic " +
        btoa(this.configuration.username + ":" + this.configuration.password);
    }
    if (this.configuration && this.configuration.apiKey) {
      headerParameters["Authorization"] =
        this.configuration.apiKey("Authorization"); // tokenAuth authentication
    }

    const response = await this.request(
      {
        path: `/user/api/v2/{id}/`.replace(
          `{${"id"}}`,
          encodeURIComponent(String(requestParameters.id))
        ),
        method: "GET",
        headers: headerParameters,
        query: queryParameters,
      },
      initOverrides
    );

    return new runtime.JSONApiResponse(response, (jsonValue) =>
      UserRetrieveFromJSON(jsonValue)
    );
  }

  /**
   */
  async userApiV2Retrieve(
    requestParameters: UserApiV2RetrieveRequest,
    initOverrides?: RequestInit
  ): Promise<UserRetrieve> {
    const response = await this.userApiV2RetrieveRaw(
      requestParameters,
      initOverrides
    );
    return await response.value();
  }

  /**
   */
  async userApiV2TokenCreateRaw(
    requestParameters: UserApiV2TokenCreateRequest,
    initOverrides?: RequestInit
  ): Promise<runtime.ApiResponse<UserToken>> {
    const queryParameters: any = {};

    const headerParameters: runtime.HTTPHeaders = {};

    headerParameters["Content-Type"] = "application/json";

    if (
      this.configuration &&
      (this.configuration.username !== undefined ||
        this.configuration.password !== undefined)
    ) {
      headerParameters["Authorization"] =
        "Basic " +
        btoa(this.configuration.username + ":" + this.configuration.password);
    }
    if (this.configuration && this.configuration.apiKey) {
      headerParameters["Authorization"] =
        this.configuration.apiKey("Authorization"); // tokenAuth authentication
    }

    const response = await this.request(
      {
        path: `/user/api/v2/token/`,
        method: "POST",
        headers: headerParameters,
        query: queryParameters,
        body: UserTokenToJSON(requestParameters.userToken),
      },
      initOverrides
    );

    return new runtime.JSONApiResponse(response, (jsonValue) =>
      UserTokenFromJSON(jsonValue)
    );
  }

  /**
   */
  async userApiV2TokenCreate(
    requestParameters: UserApiV2TokenCreateRequest = {},
    initOverrides?: RequestInit
  ): Promise<UserToken> {
    const response = await this.userApiV2TokenCreateRaw(
      requestParameters,
      initOverrides
    );
    return await response.value();
  }

  /**
   */
  async userApiV2TokenRetrieveRaw(
    initOverrides?: RequestInit
  ): Promise<runtime.ApiResponse<UserToken>> {
    const queryParameters: any = {};

    const headerParameters: runtime.HTTPHeaders = {};

    if (
      this.configuration &&
      (this.configuration.username !== undefined ||
        this.configuration.password !== undefined)
    ) {
      headerParameters["Authorization"] =
        "Basic " +
        btoa(this.configuration.username + ":" + this.configuration.password);
    }
    if (this.configuration && this.configuration.apiKey) {
      headerParameters["Authorization"] =
        this.configuration.apiKey("Authorization"); // tokenAuth authentication
    }

    const response = await this.request(
      {
        path: `/user/api/v2/token/`,
        method: "GET",
        headers: headerParameters,
        query: queryParameters,
      },
      initOverrides
    );

    return new runtime.JSONApiResponse(response, (jsonValue) =>
      UserTokenFromJSON(jsonValue)
    );
  }

  /**
   */
  async userApiV2TokenRetrieve(
    initOverrides?: RequestInit
  ): Promise<UserToken> {
    const response = await this.userApiV2TokenRetrieveRaw(initOverrides);
    return await response.value();
  }

  /**
   */
  async userApiV2UpdateRaw(
    requestParameters: UserApiV2UpdateRequest,
    initOverrides?: RequestInit
  ): Promise<runtime.ApiResponse<UserUpdate>> {
    if (requestParameters.id === null || requestParameters.id === undefined) {
      throw new runtime.RequiredError(
        "id",
        "Required parameter requestParameters.id was null or undefined when calling userApiV2Update."
      );
    }

    if (
      requestParameters.userUpdate === null ||
      requestParameters.userUpdate === undefined
    ) {
      throw new runtime.RequiredError(
        "userUpdate",
        "Required parameter requestParameters.userUpdate was null or undefined when calling userApiV2Update."
      );
    }

    const queryParameters: any = {};

    const headerParameters: runtime.HTTPHeaders = {};

    headerParameters["Content-Type"] = "application/json";

    if (
      this.configuration &&
      (this.configuration.username !== undefined ||
        this.configuration.password !== undefined)
    ) {
      headerParameters["Authorization"] =
        "Basic " +
        btoa(this.configuration.username + ":" + this.configuration.password);
    }
    if (this.configuration && this.configuration.apiKey) {
      headerParameters["Authorization"] =
        this.configuration.apiKey("Authorization"); // tokenAuth authentication
    }

    const response = await this.request(
      {
        path: `/user/api/v2/{id}/`.replace(
          `{${"id"}}`,
          encodeURIComponent(String(requestParameters.id))
        ),
        method: "PUT",
        headers: headerParameters,
        query: queryParameters,
        body: UserUpdateToJSON(requestParameters.userUpdate),
      },
      initOverrides
    );

    return new runtime.JSONApiResponse(response, (jsonValue) =>
      UserUpdateFromJSON(jsonValue)
    );
  }

  /**
   */
  async userApiV2Update(
    requestParameters: UserApiV2UpdateRequest,
    initOverrides?: RequestInit
  ): Promise<UserUpdate> {
    const response = await this.userApiV2UpdateRaw(
      requestParameters,
      initOverrides
    );
    return await response.value();
  }
}
