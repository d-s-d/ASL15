from experiment import *

#add_experiment('pingExperiment{x}_{y}',
#    node(DatabaseNode, ('dbName',), [
#        node(MiddlewareNode, ('mw{childno}',), [
#            xnode(3, DelayedClientNode, ('client{siblingno}', 'SimplePingClient', '10'),
#                {'delay': lambda t: t['childno']*2}) # start first child immediately, the second one minute later...
#        ]),
#        #node(MiddlewareNode, ('mw{childno}',), [
#        #    xnode(3, ClientNode, ('client{siblingno}', 'SimplePingClient')),
#        #]),
#    ]),
#    combinations={
#        'x': (1,2),
#        'y': (1,2)
#    }
#)

new_experiment('Ping',
    # MW
    [('mw',)],

    # CLIENTS
    lambda p: [(0, 'client{0}'.format(i), 'SimplePingClient', p['pingCount'])
        for i in xrange(p['numClients'])],

    # LEVELS
    parameters={
        'numClients': (1,2),
        'pingCount': (10,20,30)
    }
)

#add_experiment('ProdConsExp_D{durance}',
#    node(DatabaseNode, ('db',), [
#        node(MiddlewareNode, ('mw{childno}',) , [
#            node(ClientNode, ('client{siblingno}', 'OneQueueProducerClient', 'q0', '{durance}')),
#            node(DelayedClientNode, ('client{siblingno}', 'OneQueueConsumerClient', 'q0',
#                lambda t: int(t['durance']*1.5)), {'delay': '2'}),
#        ])
#    ]),
#    combinations={
#        'durance': (5,10,20)
#    }
#)


#add_experiment('GradualLoadIncrease_B{durance}',
#    node(DatabaseNode, ('db',), [
#        node(MiddlewareNode, ('mw{childno}',), [
#            xnode(2, ClientNode, ('client{siblingno}', 'OneQueueProducerClient', 'q{childno}', lambda t: int(4*t['durance']))),
#            xnode(2, DelayedClientNode, ('client{siblingno}', 'OneQueueConsumerClient', 'q{childno}', lambda t: int(4*t['durance']*2)),
#                {'delay': 2}),

#            xnode(2, ClientNode, ('client{siblingno}', 'OneQueueProducerClient', 'q{childno}', lambda t: int(3*t['durance']))),
#            xnode(2, DelayedClientNode, ('client{siblingno}', 'OneQueueConsumerClient', 'q{childno}', lambda t: int(3*t['durance']*2)),
#                {'delay': lambda t: int(t['durance']+2)}),

#            xnode(2, ClientNode, ('client{siblingno}', 'OneQueueProducerClient', 'q{childno}', lambda t: int(2*t['durance']))),
#            xnode(2, DelayedClientNode, ('client{siblingno}', 'OneQueueConsumerClient', 'q{childno}', lambda t: int(2*t['durance']*2)),
#                {'delay': lambda t: int(2*t['durance']+2)}),

#            xnode(2, ClientNode, ('client{siblingno}', 'OneQueueProducerClient', 'q{childno}', lambda t: int(1*t['durance']))),
#            xnode(2, DelayedClientNode, ('client{siblingno}', 'OneQueueConsumerClient', 'q{childno}', lambda t: int(1*t['durance']*2)),
#                {'delay': lambda t: int(3*t['durance']+2)}),
#        ]),
#        node(MiddlewareNode, ('mw{childno}',), [
#            xnode(2, DelayedClientNode, ('client{siblingno}', 'OneQueueConsumerClient', 'q{childno}', lambda t: int(4*t['durance']*2)),
#                {'delay': 2}),
#            xnode(2, ClientNode, ('client{siblingno}', 'OneQueueProducerClient', 'q{childno}', lambda t: int(4*t['durance']))),

#            xnode(2, DelayedClientNode, ('client{siblingno}', 'OneQueueConsumerClient', 'q{childno}', lambda t: int(3*t['durance']*2)),
#                {'delay': lambda t: int(t['durance']+2)}),
#            xnode(2, ClientNode, ('client{siblingno}', 'OneQueueProducerClient', 'q{childno}', lambda t: int(3*t['durance']))),

#            xnode(2, DelayedClientNode, ('client{siblingno}', 'OneQueueConsumerClient', 'q{childno}', lambda t: int(2*t['durance']*2)),
#                {'delay': lambda t: int(2*t['durance']+2)}),
#            xnode(2, ClientNode, ('client{siblingno}', 'OneQueueProducerClient', 'q{childno}', lambda t: int(2*t['durance']))),

#            xnode(2, DelayedClientNode, ('client{siblingno}', 'OneQueueConsumerClient', 'q{childno}', lambda t: int(1*t['durance']*2)),
#                {'delay': lambda t: int(3*t['durance']+2)}),
#            xnode(2, ClientNode, ('client{siblingno}', 'OneQueueProducerClient', 'q{childno}', lambda t: int(1*t['durance']))),
#        ]),
#    ]),
#    combinations={
#        'durance': (10, 20, 60, 300, 600) 
#    }
#)





