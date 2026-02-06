from flask import jsonify, request, abort
from identity.model.id import PseudoRandomIdProvider
from .. import blueprint, db
from ..decorators import validate_json
from ..model import get_api_key
from sqlalchemy import select


@blueprint.route('/create_pseudorandom_ids', methods=['POST'])
@validate_json({
    'type': 'object',
    'properties': {
        'prefix': {'type': 'string'},
        'id_count': { "type": "number", "multipleOf": 1.0, "minimum": 1 },
    },
    "required": ["prefix", "id_count"]
})
def create_pseudorandom_ids():
    id_provider = db.session.execute(select(PseudoRandomIdProvider).where(PseudoRandomIdProvider.prefix == request.json.get('prefix'))).scalars().first()

    if id_provider is None:
        abort(400)

    api_key = get_api_key(request)

    results = id_provider.allocate_ids(request.json.get('id_count'))

    barcodes = [r.barcode for r in results]

    db.session.commit()

    return jsonify({'ids': barcodes}), 201
