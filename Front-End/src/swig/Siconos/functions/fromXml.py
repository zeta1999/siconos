
import Siconos.Numerics as SN
import Siconos.Kernel as SK
import SiconosXMLParser
import numpy as np
import sys

xsdfile = '/home/chaslim/siconos/Kernel/config/xmlschema/SiconosModelSchema-V1.2.xsd'

# we should get those directly from the schema
pluginsDS = {
    'LagrangianDS': {
        'Mass': 'matrix',
        'FInt': 'vector',
        'FExt': 'vector',
        'NNL': 'vector',
        'JacobianQFInt': 'matrix',
        'JacobianVelocityFInt': 'matrix',
        'JacobianQNNL': 'matrix',
        'JacobianVelocityNNL': 'matrix'
    },
    'LagrangianLinearTIDS': {
        'K': 'matrix',
        'C': 'matrix',
        'FExt': 'vector',
    },
    'FirstOrderNonLinearDS': {
        'M': 'matrix',
        'F': 'vector',
        'JacobianFx': 'matrix'
    },
    'FirstOrderLinearDS' : {
        'A': 'matrix',
        'M': 'matrix',
        'b': 'vector'
    },
    'FirstOrderLinearTIDS' : {
        'M': 'matrix',
        'b': 'vector'
    }
}

pluginsRelation = {
    'FirstOrderRelation': {
        'h': 'pluginDef',
        'g': 'pluginDef',
        'jacobianG': 'ListOfmatrices',
        'jacobianH': 'ListOfmatrices'
    },
    'FirstOrderLinearRelation': {
        'C': 'matrix',
        'D': 'matrix',
        'F': 'matrix',
        'e': 'vector',
        'B': 'matrix'
    },
    'FirstOrderLinearTimeInvariantRelation': {
        'C': 'matrix',
        'D': 'matrix',
        'F': 'matrix',
        'e': 'vector',
        'B': 'matrix'
    },
    'LagrangianRelation': {
        'C': 'matrix'
    },
    'LagrangianLinearRelation': {
        'H': 'matrix',
        'b': 'vector',
        'D': 'matrix',
        'F': 'matrix'
    }
}


dataNSL = {
    'RelayNSL': {
        'c': 'xsd:double',
        'd': 'xsd:double',
    },
    'NewtonImpactNSL': {
        'e': 'xsd:double',
    },
    'NewtonImpactFrictionNSL': {
        'en': 'xsd:double',
        'et': 'xsd:double',
        'mu': 'xsd:double',
    },
    'ComplementarityConditionNSL': {}
}

dataOSI = {
    'MoreauJeanOSI': {
        'Theta': 'vector'
    },
    'LsodarOSI': {}
}

dataOSNSP = {
    'LCP': {},
    'FrictionContact': {},
    'QP': {
        'Q': 'matrix',
        'p': 'vector'
    },
    'Relay': {
        'M': 'matrix',
        'q': 'vector'
    }
}

# this should not even exist
relationRosetta = {
    'FirstOrderRelation' : 'FirstOrderR',
    'FirstOrderLinearRelation': 'FirstOrderLinearR',
    'FirstOrderLinearTimeInvariantRelation': 'FirstOrderLinearTIR',
    'LagrangianRelation': 'LagrangianR',
    'LagrangianLinearRelation' : 'LagrangianLinearR'
}

relationRosettaInv = {v:k for k, v in relationRosetta.items()}

nslawRosetta = {
    'Relay': 'RelayNSL',
    'NewtonImpactLaw': 'NewtonImpactNSL',
    'NewtonImpactFrictionLaw': 'NewtonImpactFrictionNSL',
    'ComplementarityCondition': 'ComplementarityConditionNSL'
}

nslawRosettaInv = {v:k for k, v in nslawRosetta.items()}

def _createVector(vec, dataType=np.float64):
    '''
    Create vector from xml data

    The data we get from the xml is horrible
    '''
    if vec.vectorFile is not None:
        return SK.SimpleVector(vec.vectorFile, True)
    else:
        return np.asarray(vec.valueOf_.split(), dtype=dataType)

def _createMatrix(mat, dataType=np.float64):
    '''
    Create matrix from xml data

    The data we get from the xml is horrible
    '''
    if mat.matrixFile is not None:
        return SK.SimpleMatrix(mat.matrixFile, True)
    else:
        return np.asarray(mat.row, dtype=dataType)

def _additionalInputsDS(dsxml, newDS, nameDS):
    dsD = dsxml.__dict__
    if dsxml.StepsInMemory is not None:
        newDS.setStepsInMemory(dsxml.StepsInMemory)
    for (plug, eltType) in pluginsDS[nameDS].items():
        if dsD[plug] is not None:
            plugin = dsD[plug]
            pluginT = eltType + 'Plugin'
            pluginStr = getattr(plugin, pluginT)
            if pluginStr is not None:
                setter = 'setCompute' + plug + 'Function'
                getattr(newDS, setter)(*pluginStr.split(':'))
            else:
                mat = globals()['_create' + eltType.title()](dsD[plug])
                setter = 'set' + plug.title() + 'Ptr'
                getattr(newDS, setter)(mat)

def _additionalInputsRelation(relxml, rel, nameRel):
    relD = relxml.__dict__
    for (plug, eltType) in pluginsRelation[nameRel].items():
        if relD[plug] is not None:
            plugin = relD[plug]
            pluginT = eltType + 'Plugin'
            pluginStr = getattr(plugin, pluginT)
            if pluginStr is not None:
                setter = 'setCompute' + plug.title() + 'Function'
                getattr(rel, setter)(pluginStr.split(':'))
            else:
                mat = globals()['_create' + eltType.title()](relD[plug])
                setter = 'set' + plug.title() + 'Ptr'
                getattr(rel, setter)(mat)

def _additionalInputsNSLaw(nslxml, nslaw, nameNSL):
    nslD = nslxml.__dict__
    for (plug, eltType) in dataNSL[nameNSL].items():
        if nslD[plug] is not None:
            setter = 'set' + plug.title()
            getattr(nslaw, setter)(nslD[plug])

def _additionalInputsOSI(osixml, osi, nameOSI):
    osiD = osixml.__dict__
    for (plug, eltType) in dataOSI[nameOSI].items():
        if osiD[plug] is not None:
            if plug == 'Theta':
                osi.setTheta(float(osiD[plug].all))
            else:
                print('Not implemented yet')

def _additionalInputsOSNSP(osnspxml, osnsp, nameOSNSP):
    osnspD = osnspxml.__dict__
    solverxml = osnspxml.NonSmoothSolver
    if solverxml is not None:
        solverOptions = osnsp.numericsSolverOptions()
        solverId = SN.nameToId(solverxml.Name)
        if solverId == 0:
            print('Error: the solver named {:} has no corresponding id in Siconos.Numerics'.format(solverxml.Name))
            exit(1)
        solverOptions.solverId = solverId
        if solverxml.dparam is not None:
            dparam = _createVector(solverxml.dparam)
            for i in range(dparam.size):
                solverOptions.dparam[i] = dparam[i]
        if solverxml.iparam is not None:
            iparam = _createVector(solverxml.iparam, np.int)
            for i in range(iparam.size):
                solverOptions.iparam[i] = iparam[i]

    for (plug, eltType) in dataOSNSP[nameOSNSP]:
        if osnspD[plug] is not None:
            setter = 'set' + plug.title() + 'Ptr'
            mat = globals()['_create' + eltType.title()](osnspD[plug])
            getattr(osnsp, setter)(mat)


# do the fucking validation
def _validateXML(xmlfile):
    etree = SiconosXMLParser.etree_
    xsd_doc = etree.parse(xsdfile)
    xsd = etree.XMLSchema(xsd_doc)
    xml = etree.parse(xmlfile)
    xsd.validate(xml)
    print(xsd.error_log)


def buildModelXML(xmlFile):
    '''
    build model from XML file given as argument
    :param: xmlFile
    '''

    # hahah lots of error
    _validateXML(xmlFile)
    #  Built DOMtree
    modelxml = SiconosXMLParser.parse(xmlFile, silence=True)

    # Load data (default value for T is -1)
    T = modelxml.Time.T
    t0 = modelxml.Time.t0
    t = modelxml.Time.t
    if t is None:
        t = t0
    title = modelxml.Title
    author = modelxml.Author
    description = modelxml.Description
    date = modelxml.Date
    xmlSchema = modelxml.SchemaXML


    # create the Model
    model = SK.Model(t0, T)
    nsdsxml = modelxml.NSDS
    nsds = model.nonSmoothDynamicalSystem()

    # NSDS
    nsds.setBVP(nsdsxml.bvp)
    allDS = {}
    for k, v in nsdsxml.DS_Definition.__dict__.items():
        if k == 'LagrangianDS':
            for ds in v:
                q0 = _createVector(ds.q0)
                v0 = _createVector(ds.Velocity0)
                newDS = SK.LagrangianDS(q0, v0)
                _additionalInputsDS(ds, newDS, k)
                nsds.insertDynamicalSystem(newDS)
                allDS[ds.number] = newDS
        elif k == 'LagrangianLinearTIDS':
            for ds in v:
                q0 = _createVector(ds.q0)
                v0 = _createVector(ds.Velocity0)
                massMatrix = _createMatrix(ds.Mass)
                newDS = SK.LagrangianLinearTIDS(q0, v0, massMatrix)
                _additionalInputsDS(ds, newDS, k)
                nsds.insertDynamicalSystem(newDS)
                allDS[ds.number] = newDS
        elif k == 'FirstOrderNonLinearDS':
            for ds in v:
                x = _createVector(ds.x0)
                newDS = SK.FirstOrderNonLinearDS(x)
                _additionalInputsDS(ds, newDS, k)
                nsds.insertDynamicalSystem(newDS)
                allDS[ds.number] = newDS
        elif k == 'FirstOrderLinearDS':
            for ds in v:
                x = _createVector(ds.x0)
                newDS = SK.FirstOrderLinearDS(x)
                _additionalInputsDS(ds, newDS, k)
                nsds.insertDynamicalSystem(newDS)
                allDS[ds.number] = newDS
        elif k == 'FirstOrderLinearTIDS':
            for ds in v:
                x = _createVector(ds.x0)
                A = _createMatrix(ds.A)
                newDS = SK.FirstOrderLinearTIDS(x, A)
                _additionalInputsDS(ds, newDS, k)
                nsds.insertDynamicalSystem(newDS)
                allDS[ds.number] = newDS
        else:
            print('DS type no known : {:}'.format(k))
            exit(1)
    if len(allDS) == 0:
        print('No DynamicalSystem found !')
        print(nsdsxml.DS_Definition.__dict__.items)
        exit(1)

    # now the Interactions
    for interxml in nsdsxml.Interaction_Definition.Interaction:
        interContent = interxml.Interaction_Content.__dict__
        for relName in pluginsRelation.keys():
            if interContent[relName] is not None:
                relxml = interContent[relName]
                if relxml.type_ is not None:  # screw this
                    relRealName = relName.replace('Relation', relxml.type_ + 'R')
                else:
                    relRealName = relationRosetta.get(relName, relName)
                relArgs = []
                if relName == 'LagrangianRelation' and 'Linear' not in relxml.type_:
                    relArgs.append(relxml.h.plugin)
                    for jac in relxml.jacobianH.matrix:
                        relArgs.append(jac.matrixPlugin)
                if relRealName == 'LagrangianLinearR':
                    relRealName = 'LagrangianLinearTIR'
                relation = getattr(SK, relRealName)(*relArgs)
                _additionalInputsRelation(relxml, relation, relName)
        for nslawName in dataNSL.keys():
            nslawOldName = nslawRosettaInv.get(nslawName, nslawName)
            if interContent[nslawOldName] is not None:
                nslxml = interContent[nslawOldName]
                nslaw = getattr(SK, nslawName)(nslxml.size)
                _additionalInputsNSLaw(nslxml, nslaw, nslawName )

        # Finally, create the Interaction and insert it in NSDS
        inter = SK.Interaction(interxml.size, nslaw, relation)
        dsVec = _createVector(interxml.DS_Concerned)
        if interxml.DS_Concerned.vectorSize == 1:
            nsds.link(inter, allDS[dsVec[0]])
        else:
            nsds.link(inter, allDS[dsVec[0]], allDS[dsVec[1]])


    # create the Simulation
    simxml = modelxml.Simulation
    if simxml.TimeDiscretisation.tk is not None:
        td = SK.TimeDiscretisation(simxml.TimeDiscretisation.tk)
    elif simxml.TimeDiscretisation.N is not None:
        td = SK.TimeDiscretisation(simxml.TimeDiscretisation.N, t0, T)
    elif simxml.TimeDiscretisation.h is not None:
        td = SK.TimeDiscretisation(t0, simxml.TimeDiscretisation.h)
    else:
        print('Could not define the TimeDiscretisation')
        exit(1)

    try:
        sim = getattr(SK, simxml.type_)(td)
    except:
        print("wrong type of simulation" + simxml.Type_)
        exit(1)

    # OSI
    allOSI = []
    for osiType in dataOSI.keys():
        for osixml in simxml.OneStepIntegrator_Definition.__dict__[osiType]:
            osi = getattr(SK, osiType)()
            _additionalInputsOSI(osixml, osi, osiType)
            dsNL = [int(s) for s in osixml.DS_Concerned.valueOf_.split()]
            for dsN in dsNL:
                osi.insertDynamicalSystem(allDS[dsN])
            sim.insertIntegrator(osi)
            allOSI.append(osi)

    # OSNSPB
    allOSNSP = []
    for osnspType in dataOSNSP.keys():
        if simxml.OneStepNSProblems_List.__dict__[osnspType] is not None:
            for osnspxml in simxml.OneStepNSProblems_List.__dict__[osnspType]:
                if osnspType is 'FrictionContact':
                    typeFC = int(osnspxml.Type)
                    osnsp = SK.FrictionContact(typeFC)
                else:
                    osnsp = getattr(SK, osnspType)()
                if osnspxml.StorageType is not None:
                    osnsp.setMStorageType(osnspxml.StorageType)
                _additionalInputsOSNSP(osnspxml, osnsp, osnspType)
                numId = SK.SICONOS_OSNSP_DEFAULT
                if osnspxml.Id is not None:
                    if simxml.type_ == 'EventDriven':
                        if osnspxml.Id == 'impact':
                            numId = SK.SICONOS_OSNSP_ED_IMPACT
                        elif osnspxml.Id == 'acceleration':
                            numId = SK.SICONOS_OSNSP_ED_SMOOTH_ACC
                        else:
                            numId = SK.SICONOS_OSNSP_ED_SMOOTH_POS
                # XXX fixme for TimeStepping
                sim.insertNonSmoothProblem(osnsp, numId)
                allOSNSP.append(osnsp)

    model.initialize(sim)
    model.display()
    nsds.display()

    return model
