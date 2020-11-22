from typing import Dict, List

from jetcart.domain import tax

from marshmallow import Schema, fields, validate, ValidationError


class TaxSchema(Schema):
    value = fields.Float(required=True)
    type = fields.Str(
        required=True,
        allow_none=False,
        validate=validate.OneOf(["C_GST", "S_GST", "VAT"])
    )


class TaxMappingSchema(Schema):
    category = fields.Str(
        required=True,
        allow_none=False,
        validate=validate.Length(min=1)
    )
    taxes = fields.List(
        cls_or_instance=fields.Str,
        required=True,
        validate=validate.Length(min=1)
    )


def create_tax(**kwargs) -> Dict:
    try:
        tax_data = TaxSchema().load(kwargs)
        return tax.create_tax(**tax_data).as_dict()
    except ValidationError as err:
        err.status_code = 400
        raise err


def fetch_tax(tax_type: str) -> Dict:
    if not tax_type:
        raise ValueError("Invalid tax type")
    tax_data = tax.get_tax_by_id(tax_type)
    if not tax_data:
        raise ValueError(f"Unknown tax type [{tax_type}]")
    return tax_data.as_dict()


def fetch_all_taxes() -> List[Dict]:
    return [
        tax_obj.as_dict()
        for tax_obj in tax.get_all()
    ]


def delete_all() -> None:
    tax.delete_all()


def create_tax_mapping(**kwargs) -> Dict:
    try:
        mapping = TaxMappingSchema().load(kwargs)
        return tax.create_tax_mapping(
            mapping['category'],
            tax_types=mapping['taxes']
        ).as_dict()
    except ValidationError as err:
        err.status_code = 400
        raise err


def fetch_all_tax_mappings() -> List[Dict]:
    return [
        mapping.as_dict()
        for mapping in tax.get_all_tax_mappings()
    ]


def fetch_tax_by_category(cat: str) -> List[Dict]:
    mapping = tax.get_tax_mapping_by_category(cat)
    if not mapping:
        raise ValueError(f"Unknown category {cat}")
    return [
        tax.get_tax_by_id(tax_type_obj.type).as_dict()
        for tax_type_obj in mapping.taxes
    ]
