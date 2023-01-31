import AddIcon from "@mui/icons-material/Add";
import ArrowDownwardIcon from "@mui/icons-material/ArrowDownward";
import ArrowUpwardIcon from "@mui/icons-material/ArrowUpward";
import DeleteOutlineIcon from "@mui/icons-material/DeleteOutline";
import GroupIcon from "@mui/icons-material/Group";
import {
  Box,
  Button,
  Checkbox,
  IconButton,
  Input,
  MenuItem,
  Select,
  TableCell,
  TableRow,
  Typography,
  ButtonTypeMap,
} from "@mui/material";
import { ExtendButtonBaseTypeMap } from "@mui/material/ButtonBase/ButtonBase";
import { IconButtonTypeMap } from "@mui/material/IconButton/IconButton";
import { OverridableComponent } from "@mui/material/OverridableComponent";
import { styled } from "@mui/material/styles";
import React, { FC, useMemo } from "react";
import { Link } from "react-router-dom";

import { aclPath } from "Routes";
import {
  Entity,
  EntityAttrUpdate,
  EntityUpdate,
} from "apiclient/autogenerated";
import { AutoCompletedField } from "components/common/AutoCompletedField";
import { AttributeTypes } from "utils/Constants";

const StyledIconButton = styled(IconButton)(({ theme }) => ({
  margin: theme.spacing(1),
})) as OverridableComponent<ExtendButtonBaseTypeMap<IconButtonTypeMap>>;

const StyledButton = styled(Button)(({ theme }) => ({
  margin: theme.spacing(1),
})) as OverridableComponent<ExtendButtonBaseTypeMap<ButtonTypeMap>>;

const NormalTableRow = styled(TableRow)(({}) => ({
  "&:nth-of-type(odd)": {
    backgroundColor: "white",
  },
  "&:nth-of-type(even)": {
    backgroundColor: "#607D8B0A",
  },
}));

const HighlightedTableRow = styled(TableRow)(({}) => ({
  "@keyframes highlighted": {
    from: {
      backgroundColor: "#6B8998",
    },
    to: {
      "&:nth-of-type(odd)": {
        backgroundColor: "white",
      },
      "&:nth-of-type(even)": {
        backgroundColor: "#607D8B0A",
      },
    },
  },
  animation: "highlighted 2s ease infinite",
}));

interface Props {
  index?: number;
  currentAttr?: EntityAttrUpdate;
  allAttrs: EntityAttrUpdate[];
  referralEntities: Entity[];
  entityInfo: EntityUpdate;
  setEntityInfo: (entityInfo: EntityUpdate) => void;
  latestChangedIndex?: number;
  setLatestChangedIndex: (latestChangedIndex: number) => void;
}

export const AttributeRow: FC<Props> = ({
  index,
  currentAttr,
  allAttrs,
  referralEntities,
  entityInfo,
  setEntityInfo,
  latestChangedIndex,
  setLatestChangedIndex,
}) => {
  const handleAppendAttribute = (nextTo: number) => {
    allAttrs.splice(nextTo + 1, 0, {
      name: "",
      type: AttributeTypes.string.type,
      isMandatory: false,
      isDeleteInChain: false,
      isDeleted: false,
      referral: [],
    });
    setEntityInfo({ ...entityInfo, attrs: [...allAttrs] });
  };

  const handleChangeOrderAttribute = (index: number, order: number) => {
    const newIndex = index - order;
    const oldIndex = index;
    const x = allAttrs[newIndex];
    allAttrs[newIndex] = allAttrs[oldIndex];
    allAttrs[oldIndex] = x;
    allAttrs[newIndex].index = index + 1 - order;
    allAttrs[oldIndex].index = index + 1;
    setLatestChangedIndex(newIndex);
    setEntityInfo({ ...entityInfo, attrs: [...allAttrs] });
  };

  const handleDeleteAttribute = (index: number) => {
    allAttrs[index] = {
      ...allAttrs[index],
      isDeleted: true,
    };
    setEntityInfo({ ...entityInfo, attrs: [...allAttrs] });
  };

  const attributeTypeMenuItems = useMemo(() => {
    return Object.keys(AttributeTypes).map((typename, index) => (
      <MenuItem key={index} value={AttributeTypes[typename].type}>
        {AttributeTypes[typename].name}
      </MenuItem>
    ));
  }, []);

  const handleChangeAttributeValue = (
    index: number,
    key: string,
    value: any
  ) => {
    allAttrs[index][key] = value;
    setEntityInfo({ ...entityInfo, attrs: [...allAttrs] });
  };

  const initialSelectedReferrals = useMemo(() => {
    return referralEntities.filter((e) =>
      currentAttr?.referral?.includes(e.id)
    );
  }, [referralEntities, currentAttr?.referral]);

  const StyledTableRow =
    index != null && index === latestChangedIndex
      ? HighlightedTableRow
      : NormalTableRow;

  return (
    <StyledTableRow onAnimationEnd={() => setLatestChangedIndex(undefined)}>
      <TableCell>
        {index !== undefined && (
          <Input
            type="text"
            value={currentAttr?.name}
            placeholder="属性名"
            sx={{ width: "100%" }}
            onChange={(e) =>
              handleChangeAttributeValue(index, "name", e.target.value)
            }
            error={currentAttr?.name === ""}
          />
        )}
      </TableCell>

      <TableCell>
        {index !== undefined && (
          <Box>
            <Box minWidth={100} marginX={1}>
              <Select
                fullWidth={true}
                value={currentAttr?.type}
                disabled={currentAttr?.id != null}
                onChange={(e) =>
                  handleChangeAttributeValue(index, "type", e.target.value)
                }
              >
                {attributeTypeMenuItems}
              </Select>
            </Box>
            {((currentAttr?.type ?? 0) & AttributeTypes.object.type) > 0 && (
              <Box minWidth={100} marginX={1}>
                <Typography>エンティティを選択</Typography>

                <AutoCompletedField
                  options={referralEntities}
                  getOptionLabel={(option: Entity) => option.name}
                  defaultValue={initialSelectedReferrals}
                  handleChangeSelectedValue={(value: Entity[]) => {
                    handleChangeAttributeValue(
                      index,
                      "referral",
                      value.map((i) => i.id)
                    );
                  }}
                  multiple
                />
              </Box>
            )}
          </Box>
        )}
      </TableCell>

      <TableCell>
        {index !== undefined && (
          <Checkbox
            checked={currentAttr?.isMandatory}
            onChange={(e) =>
              handleChangeAttributeValue(index, "isMandatory", e.target.checked)
            }
          />
        )}
      </TableCell>

      <TableCell>
        {index !== undefined && (
          <Checkbox
            checked={currentAttr?.isDeleteInChain}
            onChange={(e) =>
              handleChangeAttributeValue(
                index,
                "isDeleteInChain",
                e.target.checked
              )
            }
          />
        )}
      </TableCell>

      <TableCell>
        {index !== undefined && (
          <Box display="flex" flexDirection="column">
            <StyledIconButton
              disabled={index === 0}
              onClick={() => handleChangeOrderAttribute(index, 1)}
            >
              <ArrowUpwardIcon />
            </StyledIconButton>

            <StyledIconButton
              disabled={index === allAttrs.length - 1}
              onClick={() => handleChangeOrderAttribute(index, -1)}
            >
              <ArrowDownwardIcon />
            </StyledIconButton>
          </Box>
        )}
      </TableCell>

      <TableCell>
        {index !== undefined && (
          <StyledIconButton onClick={() => handleDeleteAttribute(index)}>
            <DeleteOutlineIcon />
          </StyledIconButton>
        )}
      </TableCell>

      {/* This is a button to add new Attribute */}
      <TableCell>
        {index !== undefined && (
          <StyledIconButton onClick={() => handleAppendAttribute(index)}>
            <AddIcon />
          </StyledIconButton>
        )}
      </TableCell>

      <TableCell>
        {index !== undefined && (
          <StyledButton
            variant="contained"
            color="primary"
            startIcon={<GroupIcon />}
            component={Link}
            to={aclPath(currentAttr?.id ?? 0)}
            disabled={currentAttr?.id == null}
          >
            ACL
          </StyledButton>
        )}
      </TableCell>
    </StyledTableRow>
  );
};
