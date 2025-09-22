package com.iflytek.stellar.console.hub.service.space;

import com.iflytek.stellar.console.commons.response.ApiResult;
import com.iflytek.stellar.console.commons.dto.space.EnterpriseAddDTO;

public interface EnterpriseBizService {

    ApiResult<Boolean> visitEnterprise(Long enterpriseId);

    ApiResult<Long> create(EnterpriseAddDTO enterpriseAddDTO);

    ApiResult<String> updateName(String name);

    ApiResult<String> updateLogo(String logoUrl);

    ApiResult<String> updateAvatar(String avatarUrl);
}
