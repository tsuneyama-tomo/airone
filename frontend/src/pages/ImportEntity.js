import { Box } from "@material-ui/core";
import Typography from "@material-ui/core/Typography";
import React from "react";
import { Link } from "react-router-dom";

import { entitiesPath, topPath } from "../Routes";
import { AironeBreadcrumbs } from "../components/common/AironeBreadcrumbs";
import { ImportForm } from "../components/common/ImportForm";
import { importEntities } from "../utils/AironeAPIClient";

export function ImportEntity({}) {
  return (
    <Box>
      <AironeBreadcrumbs>
        <Typography component={Link} to={topPath()}>
          Top
        </Typography>
        <Typography component={Link} to={entitiesPath()}>
          エンティティ一覧
        </Typography>
        <Typography>インポート</Typography>
      </AironeBreadcrumbs>

      <ImportForm importFunc={importEntities} redirectPath={entitiesPath()} />
    </Box>
  );
}
