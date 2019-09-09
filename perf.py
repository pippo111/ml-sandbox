import config as cfg

from common.model import MyModel
from common.dataset import MyDataset
from common.utils import calc_weights_generator

for setup in cfg.setups:
    # Grab dataset
    my_dataset = MyDataset(
        collection_name = cfg.dataset['collection_name'],
        batch_size = setup['batch_size'],
        limit = cfg.dataset['limit']
    )

    # Create generators
    train_generator, valid_generator, test_generator = my_dataset.create_train_valid_test_gen()
    # loss_weights = calc_weights_generator(train_generator)
    loss_weights = None
    print(loss_weights)

    # Create model
    my_model = MyModel(
            train_generator = train_generator,
            valid_generator = valid_generator,
            test_generator = test_generator,
            arch = setup['arch'],
            loss_fn = setup['loss_fn'],
            optimizer_fn = setup['optimizer_fn'],
            batch_size = setup['batch_size'],
            batch_norm = setup['batch_norm'],
            filters = setup['filters'],
            input_shape = cfg.dataset['input_shape']
        )

    my_model.create(from_weights=False, loss_weights=loss_weights)
    my_model.print_summary()

    # Train model
    my_model.train(epochs = cfg.model['epochs'])

    # Evaluate model
    my_model.evaluate()

    # Plot sample output result
    my_model.plot_result(
        coords = (cfg.logs['axis_0'], cfg.logs['axis_1'], cfg.logs['axis_2']),
        show = False, save = True
    )

    # Save results
    my_model.save_results(f'output/models/{cfg.dataset["collection_name"]}_results')
