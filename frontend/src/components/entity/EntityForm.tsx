import { Box } from "@mui/material";
import React, { FC, useEffect } from "react";

import { AttributesFields } from "./entityForm/AttributesFields";
import { BasicFields } from "./entityForm/BasicFields";
import { WebhookFields } from "./entityForm/WebhookFields";

import { Entity, EntityUpdate } from "apiclient/autogenerated";
import { DjangoContext } from "utils/DjangoContext";

interface Props {
  entityInfo: EntityUpdate;
  setEntityInfo: (entityInfo: EntityUpdate) => void;
  referralEntities?: Entity[];
  setSubmittable: (isSubmittable: boolean) => void;
}

export const EntityForm: FC<Props> = ({
  entityInfo,
  setEntityInfo,
  referralEntities,
  setSubmittable,
}) => {
  const checkSubmittable = () => {
    if (entityInfo.name === "") {
      return false;
    }
    if (
      entityInfo.attrs.filter((a) => !a.isDeleted).some((a) => a.name === "")
    ) {
      return false;
    }

    const dc = DjangoContext.getInstance();
    return !entityInfo.attrs
      .filter((a) => !a.isDeleted)
      .some(
        (a) =>
          (Number(a.type) & Number(dc.attrTypeValue.object)) > 0 &&
          a.referral.length === 0
      );
  };

  useEffect(() => {
    setSubmittable(checkSubmittable());
  });

  return (
    <Box>
      <Box>
        <Box sx={{ mb: "100px" }}>
          <BasicFields entityInfo={entityInfo} setEntityInfo={setEntityInfo} />

          <WebhookFields
            entityInfo={entityInfo}
            setEntityInfo={setEntityInfo}
          />

          <AttributesFields
            entityInfo={entityInfo}
            setEntityInfo={setEntityInfo}
            referralEntities={referralEntities}
          />
        </Box>
      </Box>
    </Box>
  );
};
